#!/usr/bin/env bash
logfile=$1
# 接口tps
## 获取tps
function getTps() {
    matchstr=$1
    result=`sudo awk -F "|" -v matchstr=$matchstr '$9==matchstr {print $1$9}' $logfile | sort|uniq -c |sort -nr -k 1|head -n 1|awk '{print $1}'`
    result=`eval echo $result`
    if [[ -z $result ]]; then
      echo 0
    else
      echo $result
    fi
}

function getTotalTps() {
    result=`sudo awk -F "|" '{print $1}' $logfile|sort|uniq -c |sort -nr -k 1|head -n 1|awk '{print $1}'`
    result=`eval echo $result`
    if [[ -z $result ]]; then
      echo 0
    else
      echo $result
    fi
}
# 统计总的tps
getTotalTps
## 统计getdisk
getTps /richlifeApp/devapp/getdisk
## 统计getDiskInfo
getTps /richlifeApp/devapp/getDiskInfo
## 统计queryCloudMember
getTps /richlifeApp/devapp/andAlbum/openApi/queryCloudMember
## 统计downloadRequest
getTps /richlifeApp/devapp/downloadRequest
## 统计UploadFileRequest
getTps /richlifeApp/devapp/pcUploadFileRequest

## 获取接口请求时间
function getRequestTime(){
  matchstr=$1
  result=`sudo awk -F "|" -v matchstr=$matchstr '$9==matchstr {print $0}' $logfile|wc -l`
  if [ $result == 0 ]; then
    echo 0
    return
  fi
  result=`sudo awk -F "|" -v matchstr=$matchstr '$9==matchstr {sum+=$3;++num} END{print (sum/num)*1000}' $logfile`
  echo $result
}
## 所有接口平均耗时
function getTotalRequestTime() {
    sudo awk -F '|' '{sum+=$3} END{print (sum/NR)*1000}' $logfile
}
# 总的耗时
getTotalRequestTime
## 统计getdisk
getRequestTime /richlifeApp/devapp/getdisk
## 统计getDiskInfo
getRequestTime /richlifeApp/devapp/getDiskInfo
## 统计queryCloudMember
getRequestTime /richlifeApp/devapp/andAlbum/openApi/queryCloudMember
## 统计downloadRequest
getRequestTime /richlifeApp/devapp/downloadRequest
## 统计UploadFileRequest
getRequestTime /richlifeApp/devapp/pcUploadFileRequest
