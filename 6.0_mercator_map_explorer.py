import geopandas as gpd
import matplotlib.widgets as wg
import matplotlib.pyplot as plt
import matplotlib.style as mplstyle
import numpy as np
from shapely.geometry import LineString
import math as m
from pyproj import Geod

mplstyle.use('fast')

world_map = r"./ne_50m_coastline_mercator_10percent/ne_50m_coastline_mercator_10percent.shp"
world_map_data = gpd.read_file(world_map)
jpn_shoreline = r"./jpn_coastline_78percent/jpn_coastline_78percent.shp"
jpn_shoreline_data = gpd.read_file(jpn_shoreline)

print(jpn_shoreline_data)

represent_lambda, represent_phi = 135, 35

y_min = -12641473.505336491 * 10
y_max = 12801473.505336491 * 10
pointer_mode = "fixed"
is_pressed = True

###地球の半径
def r():
    return  6.3781 * (10**6)

###グーデルマン関数
def gd(x):
    return 2 * m.atan(m.exp(x)) - (m.pi/2)

###経度λ(rad)からｘへ
def rad_lambda_to_x(lam):
    return r() * lam

###緯度φ(rad)からｙへ
def rad_phi_to_y(phi):
    return r() * m.log(m.tan( (m.pi/4) + (phi/2) ))

square_y_max = rad_phi_to_y(gd(m.pi))#正方形になるように切り取る

###経度λ(deg)からｘへ
def deg_lambda_to_x(lam):
    return r() * m.radians(lam)

x_max = deg_lambda_to_x(180)

###緯度φ(deg)からｙへ
def deg_phi_to_y(phi):
    return r() * m.log(m.tan( (m.pi/4) + (m.radians(phi)/2) ))

plot_x, plot_y = deg_lambda_to_x(represent_lambda), deg_phi_to_y(represent_phi)

###ｘから経度λ(rad)へ
def x_to_rad_lambda(x):
    return (1/r()) * x

###ｙから緯度φ(rad)へ
def y_to_rad_phi(y):
    return gd(y/r())

###球面座標系用の符号関数
def sgn(x):
    return 1 if x>=0 else -1

###地球上の緯度経度から三次直交座標へ変換
def spherical_to_3d(lam, phi):
    return np.array([r()*m.cos(phi)*m.cos(lam), r()*m.cos(phi)*m.sin(lam), r()*m.sin(phi)])#移動後代表点の三次直交座標

###ロドリゲスの回転公式を用いて、単位ベクトルnを軸として被回転ベクトルrをthetaラジアン回転させる
def rodrigues_rotation_formula(n, r, theta):
    return m.cos(theta)*r + (1-m.cos(theta))*(np.dot(r, n.T))*n + m.sin(theta)*(np.cross(n, r))

j = 0
distance = [[0 for i in range(len(LineString(jpn_shoreline_data["geometry"][j]).coords))] for j in range(len(jpn_shoreline_data["geometry"]))]
azimuth = [[0 for i in range(len(LineString(jpn_shoreline_data["geometry"][j]).coords))] for j in range(len(jpn_shoreline_data["geometry"]))]

geod = Geod(ellps="sphere")

for i in range(len(jpn_shoreline_data["geometry"])):
    line = LineString(jpn_shoreline_data["geometry"][i])
    for j in range(len(line.coords)):
        boundary_x, boundary_y = list(line.coords[j])[0], list(line.coords[j])[1]
        a, b, d = geod.inv(represent_lambda, represent_phi, m.degrees(x_to_rad_lambda(boundary_x)), m.degrees(y_to_rad_phi(boundary_y)))
        azimuth[i][j] = m.radians(a)
        distance[i][j] = d

def move_jpn(x_before_move, y_before_move):
    global plot_x, plot_y, jpn_shoreline_data

    ax.collections[1].remove()  # 既存の地図を削除
    coordinates, coordinates_list = [], []

    for i in range(len(jpn_shoreline_data["geometry"])):
        if i != 0:
            coordinates_list.append(coordinates)
        line = LineString(jpn_shoreline_data["geometry"][i])
        coordinates = []
        for j in range(len(line.coords)):
            plot_lambda, plot_phi = x_to_rad_lambda(plot_x), y_to_rad_phi(plot_y)                                           #移動後代表点の緯度経度
            plot_xyz_in_3d = spherical_to_3d(plot_lambda, plot_phi)                                                         #移動後代表点の三次直交座標
            n = np.array([plot_xyz_in_3d[0]/r(), plot_xyz_in_3d[1]/r(), plot_xyz_in_3d[2]/r()])                             #移動後代表点の方向に向かって伸びる大きさ１の単位ベクトル
            a = m.pi/16                                                                                                     #移動後代表点と、そこから真北へ向かって伸ばした点との隔たりを表す定数(rad)
            if plot_phi + a < m.pi/2:                                                                                       #移動後代表点から真北に向かって伸ばした点の3d座標
                point_extend_to_north = spherical_to_3d(plot_lambda, plot_phi + a)
            elif plot_phi + a > m.pi/2:
                if plot_lambda >= 0:
                    point_extend_to_north = spherical_to_3d(plot_lambda - m.pi, m.pi - (plot_phi + a))
                else:
                    point_extend_to_north = spherical_to_3d(plot_lambda + m.pi, m.pi - (plot_phi + a))
            else:#plot_phi + a == m.pi/2
                point_extend_to_north = np.array([0, 0, r()])
            peta = rodrigues_rotation_formula(n, point_extend_to_north, -azimuth[i][j])#ロドリゲスの回転公式を用いて、移動後代表点から真北に向かって伸ばした点を注目している境界点への方位角へ回す
            peta_norm = np.linalg.norm(peta, ord=2)                             #回したやつのL2ノルム
            point_extend_to_azimuth = np.array([(peta[0]/peta_norm)*r(), (peta[1]/peta_norm)*r(), (peta[2]/peta_norm)*r()])#回したやつを地球表面上に持ってくる
            vpttp = np.cross(plot_xyz_in_3d, point_extend_to_azimuth)#移動後代表点と回したやつの外積
            vpttp_norm = np.linalg.norm(vpttp, ord=2)#そいつのL2ノルム
            m_ = np.array([vpttp[0]/vpttp_norm, vpttp[1]/vpttp_norm, vpttp[2]/vpttp_norm])#移動後代表点と、求めた方位角に回した点に垂直な単位ベクトル
            boundary_xyz_in_3d = rodrigues_rotation_formula(m_, plot_xyz_in_3d, distance[i][j]/r())#移動後境界点
            boundary_x_in_3d, boundary_y_in_3d, boundary_z_in_3d = boundary_xyz_in_3d[0], boundary_xyz_in_3d[1], boundary_xyz_in_3d[2]#移動後境界点の三次直交座標
            boundary_lambda_prime, boundary_phi_prime = sgn(boundary_y_in_3d)*m.acos(boundary_x_in_3d/m.sqrt((boundary_x_in_3d**2) + (boundary_y_in_3d**2))), m.asin(boundary_z_in_3d/r())#移動後境界点の緯度経度
            boundary_x_prime, boundary_y_prime = r()*boundary_lambda_prime, r()*m.log(m.tan( (m.pi/4) + (boundary_phi_prime/2) ))#求める移動後境界点のメルカトルxy

            coordinates.append( (boundary_x_prime, boundary_y_prime) )

    coordinates_list.append(coordinates)

    line_geometries = [LineString(coordi) for coordi in coordinates_list]
    data = {"geometry": line_geometries}
    jpn_shoreline_data = gpd.GeoDataFrame(data, crs='EPSG:3395')
    ###日本の位置を更新
    jpn_shoreline_data.plot(ax=ax, color='red', linewidth=1)

    del line_geometries, coordinates, coordinates_list, line

    plt.draw()


def onclick(event):
    global pointer_mode, plot_x, plot_y, is_pressed
    if is_pressed:
        pass
    if event.xdata is None or event.ydata is None:
        return
    if pointer_mode == "fixed":
        # ポインターモードを "dragging" に切り替えて"x"印を追従させる
        pointer_mode = "dragging"
        x_before_move, y_before_move = plot_x, plot_y #更新前座標を渡す
        plot_x = np.clip(event.xdata, -x_max, x_max)
        plot_y = np.clip(event.ydata, y_min, y_max)
        ln.set_data([plot_x], [plot_y])
        move_jpn(x_before_move, y_before_move)
        plt.draw()
    else:
        pointer_mode = "fixed"

def motion(event):
    global pointer_mode, plot_x, plot_y, is_pressed
    if is_pressed:
        pass
    if pointer_mode == "dragging":
        x = event.xdata
        y = event.ydata
        if x is not None and y is not None:
            x_before_move, y_before_move = plot_x, plot_y #更新前座標を渡す
            plot_x = np.clip(x, -x_max, x_max)
            plot_y = np.clip(y, y_min, y_max)
            ln.set_data([plot_x], [plot_y])
            move_jpn(x_before_move, y_before_move)
            plt.draw()
    else:
        pointer_mode = "fixed"

def onpress(event):
    global is_pressed
    if event.key == "x":
        is_pressed = not is_pressed

fig, ax = plt.subplots(1, 1, figsize=(8, 8))
plt.subplots_adjust(left=0.04, right=1, bottom=0, top=1)
#ax.text(1.02, 0.5, "Press x to toggle plot on/off", va='center', transform=ax.transAxes, rotation=270)

world_map_data.plot(ax=ax, color='black', linewidth=0.5)
jpn_shoreline_data.plot(ax=ax, color='red', linewidth=1)

#地図の限界地点を描画 plot([x1, x2], [y1, y2])
plt.plot([-x_max, -x_max], [square_y_max, -square_y_max], color='black', linewidth=0.2)
plt.plot([x_max, x_max], [square_y_max, -square_y_max], color='black', linewidth=0.2)
#赤道を描画
plt.plot([-x_max, x_max], [0, 0], color='red', linewidth=0.8)
#目盛を非表示
plt.xticks([])
plt.yticks([])

ln, = plt.plot([], [], 'x', color='red')
ln.set_data([plot_x], [plot_y])#兵庫県明石市
plt.draw()

fig.canvas.mpl_connect('button_press_event', onclick)
fig.canvas.mpl_connect('motion_notify_event', motion)
fig.canvas.mpl_connect('key_press_event', onpress)

plt.show()
