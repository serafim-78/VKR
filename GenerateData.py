import shutil
import os
import subprocess

#путь результатов модального анализа
pathModalResult=os.getcwd()+'\\results\\antype2\\'
#длина, ширина, толщина плиты
#расстояние до трещины, ширина, глубина трещины
l=4
b=1
h=0.25
l0=1
delta=0.05 #const
#d=0.5 #0.01 +0.05 do 0.49

def WriteBaseLogs():
    k=1
    for d in range(1, 49+5, 5):
        with open('./logs/base/log%d.txt'%(k), 'w') as file:
            #задание размеров плиты
            file.write('*SET,l,'+l.__str__()+'\n*SET,b,'+b.__str__()+'\n*SET,h,'+h.__str__()+'\n')
            # задание характеристик трещины
            file.write('*SET,l0,'+l0.__str__()+'\n*SET,del,'+delta.__str__()+'\n*SET,d,'+(d/100).__str__()+'\n')
            #моделирование плиты
            file.write('/PREP7\nET,1,SOLID187\nBLOCK,,l,,b,,h,\n')
            #моделирование трещины
            file.write('K,9,l0,,,\nK,10,l0+del,,,\nK,11,l0+del/2,d,,\nK,12,l0,0,h,\nK,13,l0+del,0,h,\nK,14,l0+del/2,d,h,\nV,9,10,11,12,13,14\n')
            #вычитание объемов
            file.write('VSBV,1,2\n')
            #создание хард-поинтов
            file.write('HPTCREATE,AREA,15,0,COORD,0.1,b/2,h,\nHPTCREATE,AREA,15,0,COORD,l/4,b/2,h,\nHPTCREATE,AREA,15,0,COORD,l/2,b/2,h,\nHPTCREATE,AREA,15,0,COORD,3*l/4,b/2,h,\nHPTCREATE,AREA,15,0,COORD,l-0.1,b/2,h,\n')
            #свойства материалов
            file.write('MPTEMP,,,,,,,,\nMPTEMP,1,0\nMPDATA,EX,1,,2e10\nMPDATA,PRXY,1,,0.3\nESIZE,0.1,0,\nMPDATA,DENS,1,,2400 \n')
            #разбиение
            file.write('vmesh,all\n')
            #закрепление концов
            file.write('dl,1,,all\ndl,3,,all\n')
            k+=1

def WriteAntype(type):
    k=1
    while(os.path.exists(r'./logs/base/log%d.txt'%(k))):
        shutil.copyfile(r'./logs/base/log%d.txt'%(k), r'./logs/antype%d/log%d.txt'%(type, k))
        with open('./logs/antype%d/log%d.txt'%(type, k), 'a') as file:
            if type==2:
                #модальный анализ
                #тип анализа
                file.write('/SOL\nANTYPE,2\n')
                #настройка решателя
                file.write('MODOPT,LANB,5\nEQSLV,SPAR\nMXPAND,5, , ,0\nLUMPM,0\nPSTRES,0\nMODOPT,LANB,5,1,100, ,OFF\nsolve\n')
                #вывод первы двух резонансных частот
                file.write('/POST1\nSET,FIRST\n*GET,F1,MODE,1,FREQ\n*GET,F2,MODE,2,FREQ\n*cfopen,'+pathModalResult+'modalResult'+k.__str__()+',txt\n*vwrite,F1\n(f7.4)\n*vwrite,F2\n(f7.4)\n*cfclos\n')
            else:
                #частотный анализ
                # приложение нагрузки
                file.write('FK,17,FZ,-100000\n')
                # тип анализа
                file.write('/SOL\nANTYPE,3\n')
                # настройка решателя
                file.write('HROPT,FULL\nHROUT,OFF\nLUMPM,0\nEQSLV, ,0,\nPSTRES,0\nOUTPR,BASIC,ALL,\nHARFRQ,33,52,\nNSUBST,20,\nKBC,0\nsolve\n')
        k+=1
print(pathModalResult)

WriteAntype(2)
WriteAntype(3)
os.system(r'G:/Prpgrams/"ANSYS Inc"/v172/ansys/bin/winx64/ANSYS172.exe -b -dir G:/"pyprojects"/VKR/temp/ -i G:/"pyprojects"/VKR/logs/antype2/log1.txt -o G:/"pyprojects"/VKR/temp/out.txt')
