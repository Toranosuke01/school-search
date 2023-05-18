from bs4 import BeautifulSoup
import requests
import re
import csv
import os
from address import AddressFormatting


def school_data_output():
    # 基準地点
    base_name = input("基準地点を入力してください: ")
    base_name = base_name.replace("\uff0d", "-").replace("\xa0", "")
    base = AddressFormatting(base_name)
    radius = float(input("半径を入力してください: "))
    kind_of_school = input("校種を入力してください:")

    ns_flg = ""
    ps_flg = ""
    es_flg = ""
    js_flg = ""

    # 検索条件
    if kind_of_school == "保育園":
        ns_flg = "on"
    elif kind_of_school == "幼稚園":
        ps_flg = "on"
    elif kind_of_school == "小学校":
        es_flg = "on"
    elif kind_of_school == "中学校":
        js_flg = "on"

    gaccom_url = "https://www.gaccom.jp/search"

    prefecture = base.get_prefecture()
    municipality = base.get_municipality()

    print(prefecture)
    print(municipality)

    # now_address: 現在地
    # now_lat: 緯度
    # now_lng: 経度
    # now_pref_name: 都道府県名
    # now_city_name: 市区町村名
    # kind_ns: 保育園
    # kind_ps: 幼稚園
    # kind_es: 小学校
    # kind_js: 中学校
    # kind_flg: 校種絞り込み on/off
    # near_sort_type: 並び替え 3→距離順?
    # result_flg: 検索結果表示 on/off

    payload = {
        "now_address": "日本",
        "now_lat": base.lat,
        "now_lng": base.lng,
        "now_pref_name": prefecture,
        "now_city_name": municipality,
        "kind_ns": ns_flg,
        "kind_ps": ps_flg,
        "kind_es": es_flg,
        "kind_js": js_flg,
        "kind_flg": "on",
        "near_sort_type": "3",
        "result_flg": "result_flg",
    }

    school_index = 9
    total_student_number = 0
    unknown_student_number = 0
    total_school_number = 0
    school_list = [
        ["学校名", "生徒数", "距離（km）", "住所", "緯度", "経度", "基準地点", "基準緯度", "基準経度", "半径", "校種"]
    ]

    # SSLエラー回避
    requests.packages.urllib3.util.ssl_.DEFAULT_CIPHERS += "!DH"
    # 検索条件を送信
    search_response = requests.post(gaccom_url, data=payload, verify=False)
    search_response.encoding = search_response.apparent_encoding
    search_soup = BeautifulSoup(search_response.text, "html.parser")

    while True:
        # 学校名と距離を取得
        school_data = search_soup.select_one(
            f"#wrapper > div > div.clearfix > div > div.main > div:nth-child({school_index}) > a > div > h3 > p"
        ).text

        match = re.search(r"(.+)\(([\d.]+)(km|m)\)", school_data)
        if match:
            school_name = match.group(1)
            school_distance = float(match.group(2))
            unit = match.group(3)

            if unit == "m":
                school_distance /= 1000.0  # kmに変換

        else:
            print("Pattern not found in school_data")

        # 設定した半径を超えたら終了
        if school_distance > radius:
            print(f"半径{radius}km内の{kind_of_school}の生徒数は{total_student_number}人です。")
            print(f"生徒数が不明な学校は{unknown_student_number}校ありました。")

            school_list.append(["合計", total_student_number])

            csv_file = open(
                f"{os.environ['HOME']}/Downloads/{base_name}から半径{radius}km内の{kind_of_school}.csv",
                "w",
                encoding="shift_jis",
                newline="",
            )
            writer = csv.writer(csv_file)
            writer.writerows(school_list)
            csv_file.close()

            break

        # 検索結果最上位から順番に生徒数を分析
        student_url = search_soup.select_one(
            f"#wrapper > div > div.clearfix > div > div.main > div:nth-child({school_index}) > a"
        ).get("href")

        requests.packages.urllib3.util.ssl_.DEFAULT_CIPHERS += "!DH"
        school_response = requests.get(
            student_url.replace(".html", "/students.html"), verify=False
        )
        school_response.encoding = school_response.apparent_encoding

        school_soup = BeautifulSoup(school_response.text, "html.parser")

        student_number = school_soup.select_one(
            "#section_01 > div.box_data > table > tr:nth-child(2) > td:nth-child(2) > p"
        )
        if student_number is None:
            student_number = "不明"
        else:
            student_number = student_number.text.replace("人", "")

        # 学校の住所を取得
        school_address = school_soup.select_one(
            "#map > div > div > table > tr:nth-child(2) > td > p"
        ).text
        school_address = school_address.replace("\uff0d", "-").replace("\xa0", "")

        # 住所から座標に変換
        sc = AddressFormatting(school_address)

        print(
            f"学校名: {school_name}, 生徒数: {student_number}, 距離: {school_distance}km, 住所: {school_address}"
        )

        school_data_list = [
            school_name,
            student_number,
            school_distance,
            school_address,
            sc.lat,
            sc.lng,
            base_name,
            base.lat,
            base.lng,
            radius,
            kind_of_school,
        ]
        school_list.append(school_data_list)
        total_school_number += 1

        if student_number != "不明" and student_number != "非公開":
            total_student_number += int(student_number)
        else:
            unknown_student_number += 1

        school_index += 1


school_data_output()
