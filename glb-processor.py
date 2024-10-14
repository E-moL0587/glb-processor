import trimesh
import numpy as np

def load_glb_and_adjust_size(file_path, target_x_size):
    # GLBファイルをtrimeshでロード
    mesh = trimesh.load(file_path, force='scene')

    # メッシュに複数のジオメトリがある場合、結合する
    geometries = [geometry for geometry in mesh.geometry.values()]
    combined_mesh = trimesh.util.concatenate(geometries) if geometries else mesh

    # 元のバウンディングボックスとサイズ
    bbox_min, bbox_max = combined_mesh.bounds
    original_size = bbox_max - bbox_min

    # x方向のスケーリングファクターを計算してリサイズ
    scale_factor = target_x_size / original_size[0]
    combined_mesh.apply_scale(scale_factor)

    # スケーリング後のサイズを取得
    scaled_size = combined_mesh.bounds[1] - combined_mesh.bounds[0]

    return scaled_size[1], scaled_size[2], original_size, scaled_size

def similarity(y1, z1, y2, z2):
    # yとz方向の類似度を算出（%）
    y_similarity = 100 * (1 - abs(y1 - y2) / max(y1, y2))
    z_similarity = 100 * (1 - abs(z1 - z2) / max(z1, z2))
    return (y_similarity + z_similarity) / 2

# GLBファイルのスケール後のサイズを取得
folder_path = "models/"
glb_files = [
    "bunny.glb", "bunny_voxel.glb", "bunny_mesh.glb",
    "mibrim.glb", "mibrim_voxel.glb", "mibrim_mesh.glb",
    "guitar.glb", "house.glb", "oven.glb"
]

target_x_size = 10.0
sizes = {}

# 各ファイルのスケール後のy, zサイズを格納
for glb_file in glb_files:
    file_path = folder_path + glb_file
    y, z, original_size, scaled_size = load_glb_and_adjust_size(file_path, target_x_size)
    sizes[glb_file] = (y, z, original_size, scaled_size)

# 表のタイトル
header = (
    f"{'Label':<6}{'File':<20}{'Original X':>12} {'Original Y':>12} {'Original Z':>12}"
    f"{'Scaled X':>16} {'Scaled Y':>12} {'Scaled Z':>12} {'Top 3 Similar (Label: %)':>50}"
)
print(header)
print("=" * len(header))

# 各ファイルごとに最も似ている3つのファイルを求める
for idx, (file1, (y1, z1, original_size1, scaled_size1)) in enumerate(sizes.items()):
    similarities = []
    for id2, (file2, (y2, z2, original_size2, scaled_size2)) in enumerate(sizes.items()):
        if file1 != file2:
            sim = similarity(y1, z1, y2, z2)
            similarities.append((id2, sim))  # ID（ラベルのインデックス）と類似度を保存
    
    # 類似度の高い順に並べて、上位3つを取得
    top_3 = sorted(similarities, key=lambda x: x[1], reverse=True)[:3]
    top_3_str = '    '.join([f"{chr(65 + id2)}: {sim_pct:>6.2f}%" for id2, sim_pct in top_3])

    # 各行の結果を表示
    label = chr(65 + idx)  # A, B, C, ...
    print(
        f"{label:<6}{file1:<20}"
        f"{original_size1[0]:>12.4f} {original_size1[1]:>12.4f} {original_size1[2]:>12.4f}"
        f"{scaled_size1[0]:>16.4f} {scaled_size1[1]:>12.4f} {scaled_size1[2]:>12.4f}"
        f"{top_3_str:>50}"
    )
