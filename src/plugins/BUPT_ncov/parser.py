import json
import re
from typing import AnyStr, Dict

from bs4 import BeautifulSoup

from .exception import ParserError
from .model import REASONABLE_LENGTH, UPDATE_NEEDED_PROPS, SANITIZE_PROPS


def report_parser(html: AnyStr) -> Dict:
    soup = BeautifulSoup(html, "lxml")
    script = soup.find("script", {"src": "", "type": "text/javascript"}).get_text()
    data = re.search(r"var def = ({.*});", script)
    old_data = re.search(r"oldInfo: ({.*}),", script)
    if not data and old_data:
        raise ParserError(
            f"Failed to parse report info!\ndata: {data[1] if data else 'null'}old_data: {old_data[1] if old_data else 'null'}"
        )

    data, old_data = json.loads(data[1]), json.loads(old_data[1])
    if len(old_data) < REASONABLE_LENGTH or len(data) < REASONABLE_LENGTH:
        raise ParserError(f'Error occurred when parsing report info!\nThere is too less data in it\n'
                          f"data: {json.dumps(data, indent=2)}"
                          f"old_data: {json.dumps(old_data, indent=2)}")
    for prop in UPDATE_NEEDED_PROPS:
        if not data.get(prop, None):
            raise ParserError(f"Failed to get property {prop}!")
        old_data[prop] = data.get(prop)
    old_data.update(SANITIZE_PROPS)

    try:  # Fix Address
        if len(old_data['address']) == 0 \
                or (
                len(old_data['city']) == 0
                and old_data['province'] in ['北京市', '上海市', '重庆市', '天津市']
        ):
            geo_info = json.loads(old_data['geo_api_info'])
            old_data['address'] = geo_info['formattedAddress']
            old_data['province'] = geo_info['addressComponent']['province']
            if old_data['province'] in ['北京市', '上海市', '重庆市', '天津市']:
                old_data['city'] = geo_info['addressComponent']['province']
            else:
                old_data['city'] = geo_info['addressComponent']['city']
            old_data['area'] = ' '.join(
                [old_data['province'], old_data['city'], geo_info['addressComponent']['district']])
    except json.decoder.JSONDecodeError as e:
        raise ParserError(f'Error occurred when parsing report info!\nLocation Data can not be found!\n'
                          f'You need to checkin by yourself in order to use it!')
    return old_data


def xisu_report_parser(html: AnyStr, xisu_info: Dict) -> Dict:
    filled_form = xisu_info.get('d')
    if not isinstance(filled_form, Dict) or not filled_form.get('info') or not filled_form.get('info').get('tw'):
        raise ParserError(f'Error occurred when parsing xisu report info!\nCan not find info!\n'
                          F'You need to xisu checkin by yourself in order to use it')
    filled_form = filled_form.get('info')
    del filled_form['date']
    del filled_form['flag']
    del filled_form['uid']
    del filled_form['creator']
    del filled_form['created']
    del filled_form['id']

    data = report_parser(html)
    filled_form['area'] = data['area']
    filled_form['city'] = data['city']
    filled_form['province'] = data['province']
    filled_form['address'] = data['address']
    filled_form['geo_api_info'] = data['geo_api_info']

    return filled_form
