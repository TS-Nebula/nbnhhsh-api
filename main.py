import json,requests
from flask import Flask,render_template
app = Flask(__name__)
file = open('keywords.txt',mode='r',encoding='utf-8')
word_warehouse = file.readlines() 
file.close()
word_warehouse=[x.strip() for x in word_warehouse]
result = ""
frequency = 0
def DFA(keywords,msg):
    word_warehouse = keywords
    msg = msg

    MinMatchType = 1  # 最小匹配规则
    MaxMatchType = 2  # 最大匹配规则


    class DFAUtils(object):


        def __init__(self, word_warehouse):
            self.root = dict()
            self.skip_root = [' ', '&', '!', '！', '@', '#', '$', '￥', '*', '^', '%', '?', '？', '<', '>', "《", '》']
            for word in word_warehouse:
                self.add_word(word)

        def add_word(self, word):
            now_node = self.root
            word_count = len(word)
            for i in range(word_count):
                char_str = word[i]
                if char_str in now_node.keys():
                # 如果存在该key，直接赋值，用于下一个循环获取
                    now_node = now_node.get(word[i])
                    now_node['is_end'] = False
                else:
                # 不存在则构建一个dict
                    new_node = dict()

                    if i == word_count - 1:  # 最后一个
                        new_node['is_end'] = True
                    else:  # 不是最后一个
                        new_node['is_end'] = False

                    now_node[char_str] = new_node
                    now_node = new_node

        def check_match_word(self, txt, begin_index, match_type=MinMatchType):
            flag = False
            match_flag_length = 0  # 匹配字符的长度
            now_map = self.root
            tmp_flag = 0  # 包括特殊字符的敏感词的长度

            for i in range(begin_index, len(txt)):
                word = txt[i]

            # 检测是否是特殊字符"
                if word in self.skip_root and len(now_map) < 100:
                # len(nowMap)<100 保证已经找到这个词的开头之后出现的特殊字符
                    tmp_flag += 1
                    continue

            # 获取指定key
                now_map = now_map.get(word)
                if now_map:  # 存在，则判断是否为最后一个
                # 找到相应key，匹配标识+1
                    match_flag_length += 1
                    tmp_flag += 1
                # 如果为最后一个匹配规则，结束循环，返回匹配标识数
                    if now_map.get("is_end"):
                    # 结束标志位为true
                        flag = True
                    # 最小规则，直接返回,最大规则还需继续查找
                        if match_type == MinMatchType:
                            break
                else:  # 不存在，直接返回
                    break

            if tmp_flag < 2 or not flag:  # 长度必须大于等于1，为词
                tmp_flag = 0
            return tmp_flag

        def get_match_word(self, txt, match_type=MinMatchType):
            matched_word_list = list()
            for i in range(len(txt)):  # 0---11
                length = self.check_match_word(txt, i, match_type)
                if length > 0:
                    word = txt[i:i + length]
                    matched_word_list.append(word)
                # i = i + length - 1
            return matched_word_list

        def is_contain(self, txt, match_type=MinMatchType):
            flag = False
            for i in range(len(txt)):
                match_flag = self.check_match_word(txt, i, match_type)
                if match_flag > 0:
                    flag = True
            return flag

        def replace_match_word(self, txt, replace_char='*', match_type=MinMatchType):
            tuple_set = self.get_match_word(txt, match_type)
            word_set = [i for i in tuple_set]
            result_txt = ""
            if len(word_set) > 0:  # 如果检测出了敏感词，则返回替换后的文本
                for word in word_set:
                    replace_string = len(word) * replace_char
                    txt = txt.replace(word, replace_string)
                    result_txt = txt
            else:  # 没有检测出敏感词，则返回原文本
                result_txt = txt
            return result_txt


    if __name__ == '__main__':
      dfa = DFAUtils(word_warehouse=word_warehouse)
      # 待检测的文本
      msg = msg
      global result
      result = dfa.replace_match_word(msg)


file = open('quert.txt',mode='r',encoding='utf-8')
content = file.readlines() 
file.close()
content=[x.strip() for x in content]

@app.route('/api/search/<request>')
def api(request):
   global frequency
   frequency = frequency + 1
   existence = request in content
   
   if existence == False:
      try:
         official_api = requests.post('https://lab.magiconch.com/api/nbnhhsh/guess',data = {'text': request})
         official_api = official_api.json()
         official_api = official_api[0]
         official_api = json.dumps(official_api)
         official_api = json.loads(official_api)
         official_api = official_api['trans']
         official_api = str(official_api)
         official_api = official_api.replace("['","")
         official_api = official_api.replace("', '", " ")
         official_api = official_api.replace("']", "")
         DFA(word_warehouse,official_api)
         return '%s' % result
      except:
         return '暂无数据'
   else:
      position = content.index(request)
      position = position+1
      request = content[position] 
      return '%s' % (request)

@app.route('/api/recommend')
def Recommend():
   return render_template('post.html')

@app.route('/')
def Index():
   return render_template('index.html')

@app.route('/api/Statistics.js')
def Statistics():
   return render_template('Statistics.html',Statistics = frequency)


if __name__ == '__main__':
   app.run()