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

    # 表示用に整形（ファイル名、元のサイズ、リサイズ後のサイズ）
    result = (
        f"{file_path:<30}"
        f"{original_size[0]:>10.3f} {original_size[1]:>10.3f} {original_size[2]:>10.3f}"
        f"{scaled_size[0]:>15.3f} {scaled_size[1]:>10.3f} {scaled_size[2]:>10.3f}"
    )
    return result

# タイトルを整形して表示
header = (
    f"{'File':<30}{'Original X':>10} {'Original Y':>10} {'Original Z':>10}"
    f"{'Scaled X':>15} {'Scaled Y':>10} {'Scaled Z':>10}"
)
print(header)
print("=" * len(header))

# リサイズの基準となるxサイズ
target_x_size = 10.0

# GLBファイルがあるフォルダパス
folder_path = "models/"

# GLBファイルリスト
glb_files = [
    "bunny.glb", "bunny_voxel.glb", "bunny_mesh.glb",
    "mibrim.glb", "mibrim_voxel.glb", "mibrim_mesh.glb",
    "guitar.glb", "house.glb", "oven.glb"
]

# 各ファイルの結果を表示
for glb_file in glb_files:
    file_path = folder_path + glb_file
    print(load_glb_and_adjust_size(file_path, target_x_size))
