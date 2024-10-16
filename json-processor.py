import json
import numpy as np
import os
import time

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

    # 8つの頂点を生成
    for dx in shifts:
        for dy in shifts:
            for dz in shifts:
                corners.append([voxel_center[0] + dx, voxel_center[1] + dy, voxel_center[2] + dz])

    return np.array(corners)

# ボクセルが表面かどうかを判定する関数
def is_surface_voxel(voxel, all_voxels, size=1.0):
    half_size = size / 2
    # ボクセルの周囲に他のボクセルがあるかどうかを確認
    for dx in [-half_size, half_size]:
        for dy in [-half_size, half_size]:
            for dz in [-half_size, half_size]:
                neighbor = voxel + np.array([dx, dy, dz])
                if np.any(np.all(neighbor == all_voxels, axis=1)):  # 周囲にボクセルがある場合
                    return False
    return True  # 周囲にボクセルがなければ表面

# ボクセルとメッシュの一致率と最大距離を計算する関数
def calculate_percentage_and_max_distance(voxel_coords, mesh_coords, threshold=0.5, size=1.0):
    matches = 0
    total_surface_voxels = 0
    max_distance = 0

    for voxel_center in voxel_coords:
        if is_surface_voxel(voxel_center, voxel_coords, size):
            voxel_corners = generate_voxel_corners(voxel_center, size=size)
            # 表面のボクセルの角（頂点）のみ比較
            for corner in voxel_corners:
                total_surface_voxels += 1
                distances = np.linalg.norm(mesh_coords - corner, axis=1)
                if np.any(distances <= threshold):
                    matches += 1
                else:
                    # 一致しなかった場合の最大距離を更新
                    max_distance = max(max_distance, np.min(distances))

    percentage = (matches / total_surface_voxels) * 100 if total_surface_voxels > 0 else 0
    return percentage, max_distance

# ボクセルの体積を計算する関数
def calculate_total_volume(voxel_coords, size=1.0):
    return len(voxel_coords) * (size ** 3)

# ボクセルの表面積を計算する関数
def calculate_total_surface_area(voxel_coords, size=1.0):
    surface_voxels = [voxel for voxel in voxel_coords if is_surface_voxel(voxel, voxel_coords, size)]
    return len(surface_voxels) * (size ** 2)

# 複数のファイルを処理して一致率と最大距離を計算する関数
def process_all_files(folder_path, start=5, end=50, step=5, threshold=0.5, voxel_size=1.0):
    ref_min = np.array([0, 0, 0])
    ref_max = np.array([1, 1, 1])

    # 表のヘッダーを表示
    print(f"{'Res':<8} {'Per(%)':<12} {'Max_dis':<12} {'Matches/Total':<18} {'Total Vol':<15} {'Total Surf':<15} {'Time(s)':<15}")
    print("=" * 100)

    # 解像度ごとに処理を繰り返す
    for res in range(start, end + 1, step):
        voxel_file = f"{folder_path}/voxelCoor_res_{res}.json"
        mesh_file = f"{folder_path}/meshCoor_res_{res}.json"

        if os.path.exists(voxel_file) and os.path.exists(mesh_file):
            voxel_coords = load_coordinates(voxel_file)
            mesh_coords = load_coordinates(mesh_file)

            # スケーリング
            voxel_coords_scaled = scale_coordinates(voxel_coords, ref_min, ref_max)
            mesh_coords_scaled = scale_coordinates(mesh_coords, ref_min, ref_max)

            # 時間計測開始
            start_time = time.time()

            # 一致の割合と最大距離を計算
            percentage, max_distance = calculate_percentage_and_max_distance(voxel_coords_scaled, mesh_coords_scaled, threshold, size=voxel_size)

            # ボクセルの体積と表面積を計算
            total_volume = calculate_total_volume(voxel_coords_scaled, size=voxel_size)
            total_surface_area = calculate_total_surface_area(voxel_coords_scaled, size=voxel_size)

            # 一致した数と全表面ボクセル数も取得
            total_surface_voxels = len(voxel_coords_scaled)
            matches = int((percentage / 100) * total_surface_voxels)

            # 計算時間を取得
            elapsed_time = time.time() - start_time

            # 結果を整形して出力
            matches_total_str = f"{matches}/{total_surface_voxels}"
            matches_total_str = matches_total_str.ljust(18)

            print(f"{res:<8} {percentage:<12.2f} {max_distance:<12.4f} {matches_total_str} {total_volume:<15} {total_surface_area:<15} {elapsed_time:<15.4f}")
        else:
            # ファイルが見つからない場合
            print(f"{res:<8} {'-':<12} {'-':<12} {'Files not found':<18} {'-':<15} {'-':<15}")

folder_path = "coor_res"
threshold = 0.8  # ボクセルサイズや比較範囲に応じて変更
process_all_files(folder_path, threshold=threshold)
