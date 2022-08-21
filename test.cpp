#include <string>  
#include <jsoncpp/json/json.h>
#include <iostream>  
#include <fstream>
using namespace std;

void readFileJson()
{
	Json::Reader reader;
	Json::Value root;
 
	//从文件中读取，保证当前文件有demo.json文件  
	ifstream in("demo.json", ios::binary);
 
	if (!in.is_open())
	{
		cout << "Error opening file\n";
		return;
	}
 
	if (reader.parse(in, root))
	{
		//读取根节点信息  
		string name = root["name"].asString();
		string age = root["age"].asString();
		string sex = root["sex"].asString();
 
		cout << "My name is " << name << endl;
		cout << "I'm " << age << " years old" << endl;
		cout << "I'm a " << sex << endl;
		cout << endl;
 
		cout << "Reading Complete!" << endl;
	}
	else
	{
		cout << "parse error\n" << endl;
	}
 
	in.close();
}

int main()
{
    readFileJson();
    return 0;
}