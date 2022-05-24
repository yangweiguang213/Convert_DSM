import os
import rasterio
from rasterio.plot import show
from rasterio.warp import calculate_default_transform, reproject
from rasterio.enums import Resampling
import PySimpleGUI as sg

def convert_tif(path,upscale_factor, dst_crs = 'EPSG:4326'):
    with rasterio.open(path) as src:
        transform, width, height = calculate_default_transform(
            src.crs, dst_crs, src.width, src.height, *src.bounds)
        kwargs = src.meta.copy()
        kwargs.update({
            'crs': dst_crs,
            'transform': transform,
            'width': width,
            'height': height
        })

        if src.crs.to_string() != dst_crs:
            print("当前坐标系为：{}，需转为：{}".format(src.crs.to_string(),dst_crs))
            path = path.replace('dsm.tif','_reproject_dsm.tif')
            if os.path.exists(path):
                os.remove(path)
            with rasterio.open(path, 'w', **kwargs) as dst:
                for i in range(1, src.count + 1):
                    reproject(
                        source=rasterio.band(src, i),
                        destination=rasterio.band(dst, i),
                        src_transform=src.transform,
                        src_crs=src.crs,
                        dst_transform=transform,
                        dst_crs=dst_crs,
                        resampling=Resampling.nearest)
            print("坐标系转换完成！")
            
        with rasterio.open(path) as dataset:
            data = dataset.read(
                out_shape=(
                        dataset.count,
                        int(dataset.height * upscale_factor),
                        int(dataset.width * upscale_factor)
                    ),
                resampling=Resampling.bilinear
            )
            transform = dataset.transform * dataset.transform.scale(
                    (dataset.width / data.shape[-1]),
                    (dataset.height / data.shape[-2])
                )
            path = path.replace('dsm.tif','_resize_dsm.tif')
            if os.path.exists(path):
                os.remove(path)
            with rasterio.open(
                path,
                'w',
                driver='GTiff',
                height=data.shape[-2],
                width=data.shape[-1],
                count=1,
                dtype='float32',
                crs=dataset.crs,
                transform=transform,
            ) as dst:
                dst.write(data)
    return path

def gui():
    layout = [
        [sg.FileBrowse('选择待转换图片', key='file', target='file'), sg.Button('开始'), sg.Button('关闭')],
        [sg.Text('采样比例为:', font=("宋体", 10)), sg.InputText(size=(20, 1),key='upscale_factor',font=("宋体", 10))],
        [sg.Output(size=(50, 10))]
    ]

    window = sg.Window('dsm压缩及坐标系转换-FOR DJI', layout, font=("宋体", 10), default_element_size=(50, 1), icon='NPAAC.ico')
    while True:
        event, values = window.read()
        if event in (None, '关闭'):  # 如果用户关闭窗口或点击`关闭`
            print('关闭')
            break
        if event == '开始':
            print('开始')
            path = values['file']
            upscale_factor = float(values['upscale_factor'])
            result = convert_tif(path,upscale_factor)
            print(result)
            print('重采样完成!')
            
if __name__ == '__main__':
    gui()