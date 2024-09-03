from flask import Flask, render_template,send_from_directory
from flask import request as req
import os
import yaml
import ssl
import random
import string
import torch
import platform
import subprocess
import json
device_os=platform.platform(terse=True)
os.chdir(os.path.dirname(__file__))
os.chdir("../")
app_dir=os.getcwd()
print(f"アプリディレクトリを{app_dir}に設定しました")
print(f"起動したOS{platform.platform(terse=True)}")
app = Flask(__name__)
@app.route("/")
async def main():
    return send_from_directory(os.path.join(app_dir,"static"),"index.html")
@app.route("/<string:file_pass>")
async def file(file_pass):
    return send_from_directory(os.path.join(app_dir,"static"),file_pass)
@app.route("/img/<string:file_pass>")
async def img(file_pass):
    return send_from_directory(os.path.join(app_dir,"static/img"),file_pass)
@app.route("/js/<string:file_pass>")
async def js(file_pass):
    return send_from_directory(os.path.join(app_dir,"static/js"),file_pass)
#中身を後で実装する所一覧
@app.route("/available_device",methods=["GET"])
async def available_device():
    device_list={"NVIDIA":[],"INTEL":[],"AMD":[],"DirectML":[],"Metal":[],"CPU":[]}
    try:
        for i in range(torch.cuda.device_count()):
            device_list["NVIDIA"].append({"name":torch.cuda.get_device_name(i),"id":i})
    except:
        pass
    try:
        import intel_extension_for_pytorch # type: ignore
        for i in range(torch.xpu.device_count()):
            device_list["INTEL"].append({"name":torch.xpu.get_device_name(i),"id":i})
    except:
        pass
    try:
        import plaidml # type: ignore
        for i in range(plaidml.device_count()):
            device_list["AMD"].append({"name":plaidml.get_device_name(i),"id":i})
    except:
        pass
    try:
        import torch_directml # type: ignore
        for i in range(torch_directml.device_count()):
            device_list["DirectML"].append({"name":torch_directml.device_name(i),"id":i})
    except:
        pass
    #CPU情報に関してはOSコマンドかwindowsAPIを使用しないと取得できないためOSコマンドとwindowsAPIを使って取得する
    #Apple Silicons CPU,Radeon GPUはMetalに対応しているのでそのデバイスが見つかったらMetalに追加する
    if "Windows" in device_os:
        try:
            import wmi # type: ignore
            wmi_client = wmi.WMI()
            for cpu in wmi_client.Win32_Processor():
                device_list["CPU"].append(cpu.Name)
        except ImportError:
            print("Windows Management Instrumentationにアクセスできませんでした、正しく取得するために以下のコマンドをお試しください\npip install pywin32")
    elif "Linux" in device_os:
        return_data={}
        output=subprocess.check_output("lscpu")
        output=output.decode("utf-8")
        datas=output.split("\n")
        for data in datas:
            data.replace(" ","")
            data=data.split(":")
            try:
                return_data[data[0].lstrip()]=data[1].lstrip()
            except IndexError:
                pass
        print(return_data)
        cpu_name=return_data["Model name"]
        device_list["CPU"].append(cpu_name)
    else:
        device_info=subprocess.check_output("system_profiler SPHardwareDataType")
        #これも辞書型に変えて取得しやすいようにする
    return f"{device_list}"
@app.route("/model_upload",methods=["POST"])
async def upload():
    file_pass=[random.choice(string.ascii_letters + string.digits) for i in range(20)]
    file_pass="".join(file_pass)
    file=req.files["file"]
    file_name=file.filename
    file.save(os.path.join(app_dir,"model",file.filename))
    os.rename(os.path.join(app_dir,"model",file.filename),os.path.join(app_dir,"model",file_name))
    return file_pass
@app.route("/learning",methods=["POST"])
async def learning(request_json):

    return "Learning"
if __name__ == "__main__":
    with open("config.yaml",mode="r",encoding="UTF-8")as f:
        config = yaml.safe_load(f)
    import argparse
    parser = argparse.ArgumentParser(prog="Copy_YourSelf-Client",description='AIツール、CopyYourSelfのクライアント側のツール',usage="python3 main.py <file_Path> <options>",add_help=True)
    parser.add_argument("-a","--address",type=str,help="学習、又は推論に利用するデータを指定します。",default=config["server_ip"])
    parser.add_argument("-p","--port",type=int,help="分散学習に利用するサーバーのポートを指定します",default=config["server_port"])
    parser.add_argument("-k","--public_key",type=str,help="公開鍵を指定します",default=config["public_key_path"])
    parser.add_argument("-c","--cert",type=str,help="証明書を指定します",default=config["cert_path"])
    args = parser.parse_args()
    if args.public_key =="No" or args.cert=="No":
        app.run(host=args.address,port=args.port,debug=False)    
    else:
        context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
        context.load_cert_chain(args.cert, args.public_key)
        app.run(host=args.address,port=args.port,ssl_context=context,debug=False)