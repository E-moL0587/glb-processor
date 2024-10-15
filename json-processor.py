import json
import numpy as np
import os

# ファイルから座標データを読み込む関数
def load_coordinates(filename):
    with open(filename, 'r') as f:
        return np.array(json.load(f))

# 座標を基準範囲にスケーリングする関数
def scale_coordinates(coords, ref_min, ref_max):
    coords_min = np.min(coords, axis=0)
    coords_max = np.max(coords, axis=0)

    # 座標の範囲を[ref_min, ref_max]にスケーリング
    scale = (ref_max - ref_min) / (coords_max - coords_min)
    scaled_coords = (coords - coords_min) * scale + ref_min

    return scaled_coords

# ボクセルの中心から8つの角（頂点）を生成する関数
def generate_voxel_corners(voxel_center, size=1.0):
    half_size = size / 2
    corners = []
    shifts = [-half_size, half_size]

    for dx in shifts:
        for dy in shifts:
            for dz in shifts:
                corners.append([voxel_center[0] + dx, voxel_center[1] + dy, voxel_center[2] + dz])

    return np.array(corners)

# ボクセルが表面かどうかを判定する関数
def is_surface_voxel(voxel, all_voxels, size=1.0):
    half_size = size / 2
    # ボクセルの周囲に他のボクセルがあるかどうかを確認する
    for dx in [-half_size, half_size]:
        for dy in [-half_size, half_size]:
            for dz in [-half_size, half_size]:
                neighbor = voxel + np.array([dx, dy, dz])
                if np.any(np.all(neighbor == all_voxels, axis=1)):  # 周囲にボクセルがある場合
                    return False
    return True  # 周囲にボクセルがなければ表面

# ボクセルとメッシュの一致率を計算する関数
def calculate_percentage(voxel_coords, mesh_coords, threshold=0.5, size=1.0):
    matches = 0
    total_surface_voxels = 0

    for voxel_center in voxel_coords:
        if is_surface_voxel(voxel_center, voxel_coords, size):
            voxel_corners = generate_voxel_corners(voxel_center, size=size)
            # 表面のボクセルの角（頂点）のみ比較
            for corner in voxel_corners:
                total_surface_voxels += 1
                distances = np.linalg.norm(mesh_coords - corner, axis=1)
                if np.any(distances <= threshold):
                    matches += 1

    percentage = (matches / total_surface_voxels) * 100 if total_surface_voxels > 0 else 0
    return percentage

# 複数のファイルを処理して一致率を計算する関数
def process_all_files(folder_path, start=5, end=50, step=5, threshold=0.5, voxel_size=1.0):
    ref_min = np.array([0, 0, 0])
    ref_max = np.array([1, 1, 1])

    for res in range(start, end + 1, step):
        voxel_file = f"{folder_path}/voxelCoor_res_{res}.json"
        mesh_file = f"{folder_path}/meshCoor_res_{res}.json"

        if os.path.exists(voxel_file) and os.path.exists(mesh_file):
            voxel_coords = load_coordinates(voxel_file)
            mesh_coords = load_coordinates(mesh_file)

            # スケーリング
            voxel_coords_scaled = scale_coordinates(voxel_coords, ref_min, ref_max)
            mesh_coords_scaled = scale_coordinates(mesh_coords, ref_min, ref_max)

            # 一致の割合を計算
            percentage = calculate_percentage(voxel_coords_scaled, mesh_coords_scaled, threshold, size=voxel_size)
            print(f"Res {res}: 一致した割合: {percentage:.2f}%")
        else:
            print(f"Res {res}: ファイルが見つかりません")

folder_path = "coor_res"
threshold = 0.5  # ボクセルサイズや比較範囲に応じて変更
process_all_files(folder_path, threshold=threshold)
