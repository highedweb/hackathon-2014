import xmltodict, requests, time, json, sys

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'

f = open('d:/scratch/config.xml', 'r')

poo = xmltodict.parse(f)

config = []

def processSymbol(li):
    symbol = {}

    try:
        symbol['value'] = li['@Label']
    except:
        symbol['value'] = li['@Description']

    try:
        try:
            symbol['minVal'] = int(li['@MinimumValue'])
            symbol['maxVal'] = int(li['@MaximumValue'])
        except:
            symbol['minVal'] = float(li['@MinimumValue'])
            symbol['maxVal'] = float(li['@MaximumValue'])
    except Exception as e:
        #print(e)
        pass
        
    try:
        marker = li["esri:MarkerSymbol"]["esri:MarkerSymbol.ControlTemplate"]["ControlTemplate"]["Ellipse"]
        if marker['@Fill'].startswith('#'):
            symbol['fillColor'] = '#'+ marker['@Fill'][3:9]
        else:
            symbol['fillColor'] = marker['@Fill']

        if marker['@Stroke'].startswith('#'):
            symbol['color'] = '#'+marker['@Stroke'][3:9]
        else:
            symbol['color'] = marker['@Stroke']

        symbol['radius'] = int(marker['@Height'])

    except Exception as e: 
        filler = li["esri:SimpleFillSymbol"]
        #not a marker symbol
        symbol['fillColor'] = '#'+filler['@Fill'][3:9]
        symbol['color'] = '#'+filler['@BorderBrush'][3:9]
    
    return symbol

def processMaptip(t):
    yug = ''
    run = t['TextBlock.Inlines']['Run']
    for r in run:
        try:
            if r['@FontWeight']:
                yug+='<b>'+r['@Text']+'</b>'
        except:
            if 'Binding' in r['@Text']:
                yug +='{{{'+r['@Text'].replace('{Binding [','').replace(']}','') + '}}}'
            else:
                yug +=r['@Text']
    return yug

for i in poo['Configuration']['categories']['category']:
    cat = i['name']
    print bcolors.HEADER+cat
    for ind in i['indicators']['indicator']:
        #if ind['type']=='raster':
            #print bcolors.OKGREEN+'\t'+ind['name']
        if ind['type']=='vector':
            #print bcolors.OKBLUE+'\t'+ind['name']
            t = xmltodict.parse(ind['style'])
            legend = {'symbols':[]}
            #print json.dumps(t, sort_keys=True, indent=4)
 
            try:
                symbolField = t['esri:ClassBreaksRenderer']['@Field']
                legend['type'] = 'classBreaks'
            
                goo= t["esri:ClassBreaksRenderer"]["esri:ClassBreaksRenderer.Classes"]['esri:ClassBreakInfo']

                if type(goo) is list:
                    for li in goo:
                        symbol = processSymbol(li)
                        legend['symbols'].append(symbol)
                else:
                    symbol = processSymbol(goo)
                    legend['symbols'].append(symbol)

            except Exception as e:
                #print (e)
                symbolField = t['esri:UniqueValueRenderer']['@Field']
                legend['type']='uniqueValues'

                goo = t['esri:UniqueValueRenderer']["esri:UniqueValueRenderer.Infos"]['esri:UniqueValueInfo']

                if type(goo) is list:
                    for li in goo:
                        symbol = processSymbol(li)
                        legend['symbols'].append(symbol)
                else:
                    symbol = processSymbol(goo)
                    legend['symbols'].append(symbol)
               
            mustache = ''
            try:
                if ind['maptip'] is not None:
                    maptip = xmltodict.parse(ind['maptip'])
               
                    text = maptip['Border']['StackPanel']['TextBlock']

                    if type(text) is list:
                        for t in text:
                            mustache += processMaptip(t) +'<br/>'
                    else: mustache += processMaptip(text)

                    #remove final break
                    mustache = mustache[0:-5]
            except Exception as e:
                pass
            config.append({'name': ind['name'].replace('[','- ').replace(']','').replace('(','').replace(')',''),'url':'//gis.oregonmetro.gov/equityAtlas/data/vector/'+ind['filename'].replace('shp','zip'), 'type':'shapefile', 'symbolField': symbolField, 'source' : 'Equity Atlas', 'theme':cat, 'legend':legend, 'popupTemplate':mustache})

print json.dumps(config,sort_keys=True, indent=4)