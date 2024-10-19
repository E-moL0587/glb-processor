import json

# JSONファイルを読み込む
input_file_path = 'coor_res/voxelCoor_res_20.json'

with open(input_file_path, 'r', encoding='utf-8') as json_file:
    data = json.load(json_file)

# 変換されたリストを保持するリスト
coordinates = []

# データがリスト形式の場合、リストを変換
for coord in data:
    if isinstance(coord, list) and len(coord) == 3:
        coordinates.append({"x": coord[0], "y": coord[1], "z": coord[2]})

# 結果を辞書として構築
result = {"coordinates": coordinates}

# 出力用のJSONファイルに書き込み
output_file_path = 'output_coordinates.json'
with open(output_file_path, 'w', encoding='utf-8') as json_file:
    # JSON全体を改行して出力し、各オブジェクトは指定された形式で出力
    json_file.write('{\n  "coordinates": [\n')
    for i, coord in enumerate(coordinates):
        json_file.write(f'    {{ "x": {coord["x"]}, "y": {coord["y"]}, "z": {coord["z"]} }}')
        # 最後の要素でない場合、カンマを追加
        if i < len(coordinates) - 1:
            json_file.write(',\n')
        else:
            json_file.write('\n')
    json_file.write('  ]\n}')

print(f"変換されたデータを保存しました: {output_file_path}")
