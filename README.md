# Convert_DSM


压缩DSM并转换格式，以支持导入DJI仿地飞行


./proj/proj.db 文件夹为必要文件


打包为APP需参考convert_tif.spec修改，否则会报错


打包命令如下：
pyinstaller -F -w -i NPAAC.ico convert_tif.py