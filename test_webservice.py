from zeep import Client, Settings
settings = Settings(strict=False, xml_huge_tree=True)
client = Client('http://www.dneonline.com/calculator.asmx', settings=settings)
client.service
print(dir(client))
print(client._default_service_name)