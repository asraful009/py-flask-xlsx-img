from itertools import product
from openpyxl import Workbook
from openpyxl import load_workbook
from openpyxl_image_loader import SheetImageLoader
import threading
import io
import requests
from PIL import Image
import time
import json


def current_milli_time():
  return round(time.time() * 1000)

class Point:
  x = int(0)
  y = int(0)
  def __init__(self, x, y) -> None:
    self.x = x
    self.y = y

class ProductImageDto:
  cover = ""
  gallery = []

class ProductDto:
  name = ""
  description = ""
  summary = ""
  location = ""

  geoLocation=Point(0, 0)
  metaDescription = ""
  metaKeywords = ""
  metaTitle = ""
  reference = ""
  isApproved = 1
  isRefundable = False
  approvedBy = None
  approvedAt = None
  quantity = 0
  reserved = 0
  sold = 0
  rating = 0
  popular = 0
  trending = 0
  lowStockThreshold = 0
  price = 0
  weight = 0
  purchasedPrice = 0
  discount = 0
  wholesalePrice = 0
  additionalShippingCost = 0
  image = ProductImageDto
  onSale =  True
  isVirtual = False
  isPack: False
  productAttributes = []
  shop = ""
  category = ""
  user = ""
  merchant = ""
  cartDetails  = []
  brand = None
  productReviews =  []
  stockPurchases = []
  stockItemTransactions =[]
  coupons =[]
  freeCoupons =[]


class Product:
  token=""
  name = ""
  price = 0
  qty = 0
  cover = None

  def sendImage(self):
    with requests.Session() as s:
      img = io.BytesIO()
      headers = {
        "Authorization": f"Bearer {self.token}",
        "Connection": "close"
      }
      payload={}
      url = 'http://localhost:3105/api/image-upload/product-redis'
      
      self.cover.save(img, format=f"{self.cover.format}")
      files=[
        ('image',(f"{self.name}.{self.cover.format}", img.getvalue(), Image.MIME[self.cover.format]))
      ]
      r = s.request("POST", url, headers=headers, data=payload, files=files)
      # self.cover.save(f"{self.name}-{current_milli_time()}.{self.cover.format}", f"{self.cover.format}")
      payload = r.text
      headers["Content-Type"] = "application/json"
      url = "http://localhost:3105/api/image-upload/product"
      r = requests.request("POST", url, headers=headers, data=payload)
      print(r.text)

  def __str__(self):
    return f"{self.name}, {self.price}, {self.qty}"

class XlsImport(threading.Thread):
  products = []

  def __init__(self, xlsx, token):
    threading.Thread.__init__(self)
    wb = load_workbook(xlsx)
    ws = wb["product"]

    image_loader = SheetImageLoader(ws)
    isFirst = True
    for row in ws.iter_rows():
      if(isFirst == True) :
        isFirst = False
        continue
      product = Product()
      product.token = token
      for cell in row:
        cellkey = f"{cell.column_letter}{cell.row}"
        if image_loader.image_in(cellkey):
          # print(cellkey)
          try:
            image = image_loader.get(cellkey)
            product.cover = image
            # image.save(f"{product.name}.{image.format}", f"{image.format}")
          except Exception as e:
            print(e)
        else :
          if cell.column_letter =="B" :
            product.name = f"{cell.value}"
          elif cell.column_letter =="C" :
            product.price = float(f"{cell.value}")
          elif cell.column_letter =="D" :
            product.qty = float(f"{cell.value}")
      self.products.append(product)
    l = len(self.products)
    print(l)
    
  def run(self):
    l = len(self.products)
    print(l)
    for i in range(l):
      pro = self.products[i]
      pro.sendImage()
      print(pro)
