
import io, importlib, inspect, matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from flask import Flask, request, send_file, abort

mods={1:'modele1p',2:'modele2p',3:'modele3p',4:'modele4p'}
app=Flask(__name__)

def run_model(mid, lat, lon, year, view):
    mod=importlib.import_module(mods[mid])
    func=getattr(mod,'temp_backend',None) or getattr(mod,'temp')
    kwargs={}
    if 'lat' in func.__code__.co_varnames: kwargs['lat']=lat
    if 'lon' in func.__code__.co_varnames or 'long' in func.__code__.co_varnames: kwargs['lon']=lon
    if 'year' in func.__code__.co_varnames: kwargs['year']=year
    if 'view' in func.__code__.co_varnames: kwargs['view']=view
    return func(**kwargs)

@app.route('/run')
def run():
    try:
        mid=int(request.args.get('model',1))
        view=request.args.get('view','year')
        lat=float(request.args.get('lat',48.85))
        lon=float(request.args.get('lon',2.35))
        year=int(request.args.get('year',2024))
    except Exception:
        return abort(400,'Bad parameters')
    if mid not in mods: return abort(400,'Unknown model')
    try:
        T=run_model(mid,lat,lon,year,view)
    except Exception as e:
        return abort(500,str(e))
    fig,ax=plt.subplots(figsize=(6,2.5))
    ax.plot(T)
    ax.set_title(f'M{mid}-{view}')
    buf=io.BytesIO(); fig.savefig(buf,format='png'); plt.close(fig); buf.seek(0)
    return send_file(buf,mimetype='image/png')

@app.route('/')
def ok(): return 'CREPSITE backend OK'

if __name__=='__main__':
    app.run(debug=True,port=5000)
