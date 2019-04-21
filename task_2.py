import cv2
from matplotlib import pyplot as plt
import onvif
import zeep
import config
import copy
import threading


rtsp_42 = "rtsp://192.168.15.42:554/Streaming/Channels/101?transportmode=unicast&profile=Profile_1"

def auto(ip, port):
    #Подключаемся к камере
    mycam = onvif.ONVIFCamera(ip, port, config.login, config.password, config.way)

    #Без кода ниже не работает
    def zeep_pythonvalue(self, xmlvalue):
        return xmlvalue

    zeep.xsd.simple.AnySimpleType.pythonvalue = zeep_pythonvalue

    # Создаём сервис media
    media = mycam.create_media_service()

    # Получаем Media Profile
    media_profile = media.GetProfiles()[0]

    #Создаём сервис для работы с изображением
    image = mycam.create_imaging_service()

    #Формируем запрос, с помощью которого будем получатьтекущие параметры съёмки
    request_get = image.create_type('GetImagingSettings')
    request_get.VideoSourceToken = media_profile.VideoSourceConfiguration.SourceToken

    #Получаем текущие параметры съёмки
    image_settings = image.GetImagingSettings(request_get)

    # Создаём запрос, с помошью которого будем менять параметры съёмки
    request_set = copy.deepcopy(request_get)

    # Говорим камере, что мы сами корректировать цвет
    image_settings.WhiteBalance.Mode = 'MANUAL'
    request_set.ImagingSettings = image_settings
    image.SetImagingSettings(request_set)

    image_settings = image.GetImagingSettings(request_get)

    #Задаём настройки баланса белого
    image_settings.WhiteBalance.CrGain = 80
    image_settings.WhiteBalance.CbGain = 40

    request_set.ImagingSettings = image_settings
    image.SetImagingSettings(request_set)

def auto_2():
    # Подключаемся к камере
    mycam = onvif.ONVIFCamera(config.ip_42, config.port_42, config.login, config.password, config.way)

    # Без кода ниже не работает
    def zeep_pythonvalue(self, xmlvalue):
        return xmlvalue

    zeep.xsd.simple.AnySimpleType.pythonvalue = zeep_pythonvalue

    # Создаём сервис media
    media = mycam.create_media_service()

    # Получаем Media Profile
    media_profile = media.GetProfiles()[0]

    # Получаем кадр с видео
    cap = cv2.VideoCapture(rtsp_42)

    # Получаем из кадра изображение
    ret, img = cap.read()

    hist = plt.hist(img.ravel(), 256, [0, 256])

    # Озвобождаем не нужную память
    cap.release()

    # Создаём сервис для работы с изображением
    image = mycam.create_imaging_service()

    # Формируем запрос, с помощью которого будем получатьтекущие параметры съёмки
    request_get = image.create_type('GetImagingSettings')
    request_get.VideoSourceToken = media_profile.VideoSourceConfiguration.SourceToken

    # Получаем текущие параметры съёмки
    image_settings = image.GetImagingSettings(request_get)

    print(image_settings)

    # Создаём запрос, с помошью которого будем менять параметры съёмки
    request_set = copy.deepcopy(request_get)

    # Говорим камере, что мы сами будем регулировать экспозицию и корректировать цвет
    image_settings.Exposure.Mode = 'MANUAL'
    image_settings.WhiteBalance.Mode = 'MANUAL'
    request_set.ImagingSettings = image_settings
    image.SetImagingSettings(request_set)

    image_settings = image.GetImagingSettings(request_get)

    gain = 0

    # Задаём настройки баланса белого
    image_settings.WhiteBalance.CrGain = 80
    image_settings.WhiteBalance.CrGain = 40

    request_set.ImagingSettings = image_settings
    image.SetImagingSettings(request_set)


    # Создаём список значений, которые может принимать выдержка
    ex_time = [33.0, 100.0, 166.0, 285.0, 400.0, 571.0, 800.0, 1000.0, 1666.0, 2352.0, 3333.0, 4000.0, 4444.0, 5000.0,
               5714.0, 6666.0, 8333.0, 10000.0, 13333.0, 20000.0, 40000.0]

    while (True):
        # Строим гистограмму полученного изображения
        cap = cv2.VideoCapture(rtsp_42)
        ret, frame = cap.read()
        cap.release()
        hist = plt.hist(frame.ravel(), 256, [0, 256])
        plt.show()
        print(hist[0][128])
        while (hist[0][128] < 8000.0):  # Проверяем, достаточно ли яркие полутона, если нет то идём дальше по услловию
            if (image_settings.Exposure.ExposureTime < 40000.0):  # Проверяем, максимальное ли значение имеет выдержка
                # time += 2667
                cur_ind = ex_time.index(image_settings.Exposure.ExposureTime)
                # image_settings.Exposure.ExposureTime = time
                # request_set.ImagingSettings = image_settings
                # image.SetImagingSettings(request_set)
                # image_settings = image.GetImagingSettings(request_get)

                if (ex_time[cur_ind] < 10000):
                    image_settings.Exposure.ExposureTime = 10000
                else:
                    image_settings.Exposure.ExposureTime = ex_time[cur_ind + 1]
                    request_set.ImagingSettings = image_settings
                    image.SetImagingSettings(request_set)
                    image_settings = image.GetImagingSettings(request_get)

                cap = cv2.VideoCapture(rtsp_42)
                ret, frame = cap.read()
                cap.release()
                hist = plt.hist(frame.ravel(), 256, [0, 256])
                print('H', hist[0][128])

            else:
                gain += 7
                image_settings.Exposure.Gain = gain
                request_set.ImagingSettings = image_settings
                image.SetImagingSettings(request_set)
                image_settings = image.GetImagingSettings(request_get)

                cap = cv2.VideoCapture(rtsp_42)
                ret, frame = cap.read()
                cap.release()
                hist = plt.hist(frame.ravel(), 256, [0, 256])
                print('H', hist[0][128])

        while (hist[0][128] > 80000.0):  # Проверяем, достаточно ли яркие полутона, если нет то идём дальше по услловию
            if image_settings.Exposure.Gain > 0:
                gain -= 7
                image_settings.Exposure.Gain = gain
                request_set.ImagingSettings = image_settings
                image.SetImagingSettings(request_set)
                image_settings = image.GetImagingSettings(request_get)

                cap = cv2.VideoCapture(rtsp_42)
                ret, frame = cap.read()
                cap.release()
                hist = plt.hist(frame.ravel(), 256, [0, 256])
                print('D', hist[0][128])
            else:
                # time -= 2667
                cur_ind = ex_time.index(image_settings.Exposure.ExposureTime)
                # image_settings.Exposure.ExposureTime = time
                # request_set.ImagingSettings = image_settings
                # image.SetImagingSettings(request_set)
                # image_settings = image.GetImagingSettings(request_get)
                #

                print('D', hist[0][128])
                image_settings.Exposure.ExposureTime = ex_time[cur_ind - 1]
                request_set.ImagingSettings = image_settings
                image.SetImagingSettings(request_set)
                image_settings = image.GetImagingSettings(request_get)

                cap = cv2.VideoCapture(rtsp_42)
                ret, frame = cap.read()
                cap.release()
                hist = plt.hist(frame.ravel(), 256, [0, 256])



#Создаём несколько потоков для работы с нескольками камерами одновременно
threading.Thread(target=auto, args=(config.ip_43, config.port_43)).start()
threading.Thread(target=auto, args=(config.ip_45, config.port_45)).start()
threading.Thread(target=auto_2).start()
