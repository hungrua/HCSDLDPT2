import json
from audioScaledFeature import ScaledAudio
from cluster import Cluster
from getAudioFeature import getAllFeature
from scaleData import getMinMax

def jsonToScaledAudioOb(json_data):
    name = json_data['Name']
    scaled_features = [json_data[key] for key in ['RMS', 'ZCR', 'Silence Ratio', 'Bandwidth', 'Centroid'] +
                      [f'Mfcc{i}' for i in range(1, 13)]]
    return ScaledAudio(name,scaled_features)

def jsonToClusterObject(json_cluster_data):
    name = json_cluster_data['Name']
    
    scaled_features = [json_cluster_data['Centroid'][key] for key in ['RMS', 'ZCR', 'Silence Ratio', 'Bandwidth', 'Centroid'] +
                      [f'Mfcc{i}' for i in range(1, 13)]]
    centroid = scaled_features
    child = []
    listChild = json_cluster_data['child']
    for childJson in listChild:
        child.append(jsonToScaledAudioOb(childJson))
    
    return Cluster(name,centroid,child)
    

if __name__ == '__main__':
    #Lấy file audio
    fileName = "Engtest1.wav"
    
    #Trích xuất ra các đặc trưng của file audio
    findingFiles = getAllFeature(fileName)
    
    #Scale dữ liệu đầu vào
    minmax = getMinMax("./resultData/result.csv")
    findingFiles.getScaledArr(minmax)
    findingScaledAudio = ScaledAudio(fileName,findingFiles.scaled)
    
    #Lấy dữ liệu các cụm sau khi phân cụm từ file JSON
    clusters = []
    with open('./resultData/clusters.json') as f:
        data = json.load(f)
    for dt in data:
        clusters.append(jsonToClusterObject(dt))
    
    #Tính khoảng cách đến tâm của các cụm
    distancesToCentroid = []
    for cluster in clusters:
        distance ={}
        distance['cluster'] = cluster.name
        distance['distanceToCentroid'] = findingScaledAudio.distance(cluster.centroid)
        distance['child'] = cluster.child
        distancesToCentroid.append(distance)
    threeNearstAudio = []
    
    #Sắp xếp các cụm theo khoảng cách từ tâm đến audio đang xét tăng dần
    sorted_distance = sorted(distancesToCentroid, key=lambda x: x['distanceToCentroid'])
    
    #Duyệt từng cụm theo thứ tự khoảng cách tăng dần
    for d in sorted_distance:
        k = len(threeNearstAudio)  
        #Nếu độ dài file kq >=3 thì dừng tìm kiếm  
        if(k>=3):
            break
        
        distanceToAudio = []
        # Xét từng file audio trong cụm sau đó tính khoảng cách Euclide với file audio đang xét
        for audio in d['child']:
            distanceToPoint = {}
            distanceToPoint['name'] = audio.name
            distanceToPoint['distanceToAudio'] = findingScaledAudio.distance(audio)
            distanceToAudio.append(distanceToPoint)
        #Sắp xếp lại theo thứ tự khoảng cách tăng dần
        sorted_distanceToAudio =sorted(distanceToAudio, key=lambda x: x['distanceToAudio'])
        
        #Nếu số lượng audio trong cụm bé hơn hoặc bằng 3 thực hiện thêm tất cả audio trong cụm đó vào mảng kq
        if len(sorted_distanceToAudio) <=3 :
            threeNearstAudio= sorted_distanceToAudio.copy()
            threeNearstAudio.extend(sorted_distanceToAudio[:(3-k)])
        
        #Nếu số lượng audio trong cụm lớn hơn thì chỉ thêm 3-k phần tử còn thiếu vào trong mảng kq
        else :
            threeNearstAudio.extend(sorted_distanceToAudio[:(3-k)])
    #In ra tên và khoảng cách của 3 file audio tương đồng nhất
    for audio in threeNearstAudio:
        print(audio['name'], audio['distanceToAudio'])
            
                