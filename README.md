# ��ʪ�ȼ��ϵͳ

����һ������Raspberry Pi����ʪ�ȼ��ϵͳ��ʹ��DHT11�������ɼ���ʪ�����ݣ�ͨ��OLED��Ļ��ʾ�����������ϴ���Web������չʾ��ʪ������ͼ��

## �����ص�

- ʹ��DHT11�������ɼ���ʪ������
- ��OLED��Ļ��ʵʱ��ʾ�¶Ⱥ�ʪ��
- ���ɼ��������ϴ���Web������
- Webҳ��չʾ��ʪ��ʵʱ����ͼ
- ���ݶ�ʱ�Զ�ˢ��

## Ӳ������

- Raspberry Pi (�κ��ͺŶ�����)
- DHT11��ʪ�ȴ�����
- SSD1306 OLED��ʾ�� (128x64����)
- ������

## ����˵��

DHT11����:
- VCC -> 3.3V
- GND -> GND
- DATA -> GPIO4 (����dht11.py���޸�)

OLED����:
- VCC -> 3.3V
- GND -> GND
- SCL -> GPIO SCL
- SDA -> GPIO SDA

## �������

```bash
pip install adafruit-circuitpython-dht
pip install adafruit-circuitpython-ssd1306
pip install pillow
pip install flask
pip install requests
```

## ʹ�÷���

1. ���ս���˵������DHT11��������OLED��ʾ��
2. ��װ������������
3. ����Web������

```bash
python server.py
```

4. ����һ���ն�����������

```bash
python main.py
```

5. ����������� `http://localhost:5000` �鿴��ʪ������ͼ

## �ļ�˵��

- `dht11.py`: DHT11��������������
- `oled.py`: OLED��ʾ����������
- `main.py`: ���������ϴ�������ȡ����ʾ����
- `server.py`: Web�����������պʹ洢����
- `templates/index.html`: Webҳ��ģ�壬��ʾ��ʪ������ͼ
- `sensor_data.json`: ���ݴ洢�ļ�

## ע������

- DHT11����������������Ϊ1Hz�������ȡ�����С��2��
- �����������ʣ���������������ʱ���ú��ʵ������Ͷ˿ڣ���������Ӧ�����簲ȫ����
- ���ݴ洢Ĭ����ౣ��1000����¼������server.py���޸� 