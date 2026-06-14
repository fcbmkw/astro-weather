import streamlit as st
import requests
from datetime import datetime, timedelta, timezone
import folium
from streamlit_folium import st_folium
import pandas as pd
import altair as alt
import math
import ephem

# --- CƠ SỞ DỮ LIỆU ĐỊA ĐIỂM ---
LOCATION_DATABASE = {
    "1. Jogashima 馬の背, Kanagawa": [35.1313, 139.6179],
    "2. Tateyama ゴルフ場, Chiba": [34.9517, 139.8103],
    "3. Shirahama 白浜の屏風岩, Chiba": [34.9088, 139.8294],
    "4. Onjuku 大波月海岸, Chiba": [35.1795, 140.3729],
    "5. Isumi 雀島, Chiba": [35.3196, 140.4091],
    "6. Manazuru 真鶴岬, Kanagawa": [35.1408, 139.1609],
    "7. Shimoda 灯台, Shizuoka": [34.6588, 138.9868],
    "8. Cape Aiai 愛の鐘, Shizuoka": [34.6073, 138.8284],
    "9. Matsuzaki 千貫門ビーチ, Shizuoka": [34.7213, 138.7431],
    "10. Okuoikojo 奥大井湖上駅展望台, Shizuoka": [35.1704, 138.1811],
    "11. Asagiri Plateau 朝霧高原, Shizuoka": [35.4224, 138.5927],
    "12. Shoji-ko, Yamanashi": [35.4912, 138.6049],
    "13. Hanamomo-no-sato, Nagano": [35.4457, 137.6617],
    "14. Ontake 御嶽山, Nagano": [35.8989, 137.4887],
    "15. Kamikochi 上高地, Nagano": [36.2502, 137.6392],
    "16. Enzan-so 燕山荘/イルカ岩, Nagano": [36.3991, 137.7151],
    "17. Utsukushihara 美ヶ原, Nagano": [36.2274, 138.1296],
    "18. JAXA宇宙アンテナ, Nagano": [36.1408, 138.3537],
    "19. カラマツの丘 Tsumagoi, Gunma": [36.4773, 138.4646],
    "20. Yugama/Shibutoge 渋峠, Gunma": [36.6534, 138.5274],
    "21. Sakura 上発知のシダレザクラ, Gunma": [36.7325, 139.0601],
    "22. Oku-Nikko 湯ノ湖畔, Tochigi": [36.8036, 139.4236],
    "23. Hoshinomura 天地人橋, Fukushima": [37.3427, 140.6756],
    "24. Azuma-kofuji 浄土平, Fukushima": [37.7230, 140.2551],
    "25. Okama 御釜, Zao, Miyagi": [38.1361, 140.4468],
    "26. Higashinamekawa 東滑川海浜緑地, Ibaraki": [36.6144, 140.6802],
    "27. Okutama 奥多摩湖, Tokyo": [35.7920, 139.0475],
    "28. Choshi Inubosaki 犬吠埼灯台, Chiba": [35.7077, 140.8685],
    "29. Kujukuri Beach 九十九里浜, Chiba": [35.5002, 140.4315],
    "30. Awa Shirahama 安房白浜港灯台, Chiba": [34.9146, 139.9355],
    "31. Oarai Isosaki 神磯の鳥居, Ibaraki": [36.3151, 140.5894],
    "32. Fukuroda Falls 袋田の滝, Ibaraki": [36.7641, 140.4062],
    "33. Plateau Satomi プラトーさとみ, Ibaraki": [36.7992, 140.5364],
    "34. Oze Numata 尾瀬ヶ原, Gunma": [36.9306, 139.2150],
    "35. Tanbara Highlands 玉原高原, Gunma": [36.7833, 139.0830],
    "36. Chichibu Misotsuchi 三十槌氷柱周辺, Saitama": [35.9563, 138.9255],
    "37. Nakatsu Gorge 中津峡, Saitama": [35.9977, 139.0124],
    "38. Kozushima Maehama 前浜海岸, Tokyo": [34.2086, 139.1358],
    "39. Mikurajima Observatory 御蔵島展望地, Tokyo": [33.8740, 139.5950],
    "40. Hachijojima Nambara 南原千畳岩海岸, Tokyo": [33.1003, 139.7706],
    "41. Yamanakako Panorama 山中湖パノラマ台, Yamanashi": [35.4154, 138.8758],
    "42. Kiyosato Seisenryo 清泉寮, Yamanashi": [35.9245, 138.4214],
    "43. Misaka Pass 御坂峠, Yamanashi": [35.5493, 138.7090],
    "44. Nobeyama Radio Observatory 野辺山, Nagano": [35.9414, 138.4704],
    "45. Takabocchi Highlands 高ボッチ高原, Nagano": [36.1045, 138.0170],
    "46. Soni Highlands 曽爾高原, Nara": [34.5346, 136.1506],
    "47. Norikura Tatamidaira 乗鞍畳平, Gifu": [36.1068, 137.5538],
    "48. Hirayu Pass 平湯峠, Gifu": [36.1808, 137.5303],
    "49. Shinhotaka Ropeway 新穂高, Gifu": [36.2854, 137.5743],
    "50. Shirakawago, Gifu": [36.2573, 136.9060],
    "51. Chirihama Beach 千里浜なぎさドライブウェイ, Ishikawa": [36.8157, 136.7448],
    "52. Mikatagoko Rainbow Line 三方五湖, Fukui": [35.5945, 135.8824],
    "53. Kumano Oni-ga-jo 鬼ヶ城, Mie": [33.8930, 136.1113],
    "54. Daiozaki Lighthouse 大王崎, Mie": [34.2708, 136.8964],
    "55. Odaigahara Driveway 大台ヶ原, Nara": [34.1856, 136.1090],
    "56. Tenkawa Miroku Pass 天川村, Nara": [34.2460, 135.8680],
    "57. Nishiharima Observatory 西はりま天文台, Hyogo": [35.0258, 134.3553],
    "58. Bisei Observatory 美星天文台, Okayama": [34.6712, 133.5483],
    "59. Hiruzen Highlands 蒜山高原, Okayama": [35.2770, 133.6740],
    "60. Tottori Sand Dunes 鳥取砂丘, Tottori": [35.5397, 134.2383],
    "61. Misasa Onsen 三朝温泉周辺, Tottori": [35.4105, 133.8924],
    "62. Akiyoshidai Karst 秋吉台, Yamaguchi": [34.2576, 131.3070],
    "63. Shikoku Karst 四国カルスト, Ehime": [33.3804, 132.9536],
    "64. Ashizuri Cape 足摺岬, Kochi": [32.7196, 133.0182],
    "65. Sata Cape 佐多岬, Kagoshima": [30.9924, 130.6595], 
    "66. Aso Kusasenri 草千里ヶ浜, Kumamoto": [32.8845, 131.0808],
    "67. Daikanbo 大観峰, Kumamoto": [32.99963, 131.0671],
    "68. Ikitsuki Island 生月島, Nagasaki": [33.3720, 129.3988],
    "69. Yobuko Cape Hado 波戸岬, Saga": [33.5528, 129.8527],
    "70. Amaterasu Railway 高千穂, Miyazaki": [32.7147, 131.3083],
    "71. Cape Toi 都井岬, Miyazaki": [31.3674, 131.3458],
    "72. Kaimondake 開聞岳周辺, Kagoshima": [31.1805, 130.5284],
    "73. Yoron Island 百合ヶ浜, Kagoshima": [27.0452, 128.4246],
    "74. Ishigaki Hirakubozaki 平久保崎, Okinawa": [24.6053, 124.3427],
    "75. Tamatorizaki Observatory 玉取崎展望台, Okinawa": [24.4553, 124.2520],
    "76. Iriomote Hoshizuna Beach 星砂の浜, Okinawa": [24.4078, 123.7575],
    "77. Hateruma Observatory 波照間島, Okinawa": [24.0558, 123.8060],
    "78. Cape Zanpa 残波岬, Okinawa": [26.4360, 127.7045],
    "79. Kouri Bridge 古宇利大橋, Okinawa": [26.7069, 128.0188],
    "80. Cape Hedo 辺戸岬, Okinawa": [26.8716, 128.2695],
    "81. Miyakojima Higashi-Hennazaki 東平安名崎, Okinawa": [24.7353, 125.4672],
    "82. Kurima Bridge 来間大橋, Okinawa": [24.7248, 125.2478],
    "83. Aogashima Observatory 青ヶ島展望公園, Tokyo": [32.4542, 139.7618],
    "84. Niijima Habushiura 羽伏浦海岸, Tokyo": [34.3872, 139.2878],
    "85. Shikinejima Tomari Beach 泊海岸, Tokyo": [34.3265, 139.2158],
    "86. Ogasawara Weather Station 小笠原, Tokyo": [27.0944, 142.1917],
    "87. Kirigamine Highlands 霧ヶ峰, Nagano": [36.1030, 138.1946],
    "88. Shirakoma Pond 白駒池, Nagano": [36.0510, 138.3597],
    "89. Yachiho Plateau 八千穂高原, Nagano": [36.0694, 138.3806],
    "90. Senjojiki Cirque 千畳敷カール, Nagano": [35.7725, 137.8173],
    "91. Happo Pond 八方池, Nagano": [36.6940, 137.7844],
    "92. Tsugaike Nature Park 栂池自然園, Nagano": [36.7582, 137.8758],
    "93. Hakuba Iwatake 白馬岩岳, Nagano": [36.7167, 137.8594],
    "94. Shiga Highlands 志賀高原, Nagano": [36.7172, 138.5177],
    "95. Mt. Myoko 妙高高原, Niigata": [36.8917, 138.1708],
    "96. Yahiko Skyline 弥彦山, Niigata": [37.7052, 138.8178],
    "97. Senami Coast 瀬波海岸, Niigata": [38.2410, 139.4628],
    "98. Gassan Hachigome 月山八合目, Yamagata": [38.5484, 140.0264],
    "99. Toriumi Observatory 鳥海山鉾立, Akita": [39.0933, 140.0497],
    "100. Cape Tappi 龍飛崎, Aomori": [41.2570, 140.3495],
    
    "101. Cape Notoro 能取岬, Hokkaido": [44.0174, 144.2740],
    "102. Lake Mashu 摩周湖, Hokkaido": [43.5763, 144.5360],
    "103. Bihoro Pass 美幌峠, Hokkaido": [43.7398, 144.2570],
    "104. Lake Kussharo 屈斜路湖, Hokkaido": [43.6110, 144.3320],
    "105. Cape Kiritappu 霧多布岬, Hokkaido": [43.0808, 145.1174],
    "106. Cape Erimo 襟裳岬, Hokkaido": [41.9272, 143.2473],
    "107. Notsuke Peninsula 野付半島, Hokkaido": [43.5765, 145.2765],
    "108. Lake Saroma サロマ湖, Hokkaido": [44.1257, 143.9060],
    "109. Shiretoko Pass 知床峠, Hokkaido": [44.0702, 145.1110],
    "110. Cape Kamui 神威岬, Hokkaido": [43.3318, 140.3495],
    "111. Omazaki 大間崎, Aomori": [41.5265, 140.9125],
    "112. Hotokegaura 仏ヶ浦, Aomori": [41.3273, 140.8365],
    "113. Lake Towada 十和田湖, Aomori": [40.4405, 140.8885],
    "114. Hakkoda 八甲田山, Aomori": [40.6530, 140.8770],
    "115. Nyuto Onsen 乳頭温泉郷, Akita": [39.7992, 140.8020],
    "116. Tazawako 田沢湖, Akita": [39.7264, 140.6954],
    "117. Oga Nyudozaki 入道崎, Akita": [39.9922, 139.7105],
    "118. Jodogahama 浄土ヶ浜, Iwate": [39.6440, 141.9800],
    "119. Kitayamazaki 北山崎, Iwate": [40.0715, 141.9472],
    "120. Ryusendo 龍泉洞周辺, Iwate": [39.8442, 141.8370],
    "121. Naruko Gorge 鳴子峡, Miyagi": [38.7480, 140.7190],
    "122. Izunuma 伊豆沼, Miyagi": [38.7350, 141.1030],
    "123. Mt. Haguro 羽黒山, Yamagata": [38.7025, 139.9838],
    "124. Funagata-yama 船形山展望台, Miyagi": [38.6430, 140.5870],
    "125. Tadami Bridge 只見線第一橋梁, Fukushima": [37.3445, 139.3150],
    "126. Goshikinuma 五色沼, Fukushima": [37.6550, 140.0720],
    "127. Inawashiro Lake 猪苗代湖, Fukushima": [37.5460, 140.1040],
    "128. Amaharashi Coast 雨晴海岸, Toyama": [36.8174, 137.0452],
    "129. Tateyama Murodo 室堂, Toyama": [36.5776, 137.6064],
    "130. Shogawa Gorge 庄川峡, Toyama": [36.5860, 136.9710],
    "131. Mitsukejima 見附島, Ishikawa": [37.3961, 137.2474],
    "132. Senmaida 白米千枚田, Ishikawa": [37.4252, 136.9996],
    "133. Rokkozaki 禄剛崎, Ishikawa": [37.5289, 137.3261],
    "134. Hakusan Chokaisanso 白山チブリ尾根避難小屋, Ishikawa": [36.1560, 136.7490],
    "135. Ena Ravine Bridge 恵那峡大橋展望台, Gifu": [35.4859, 137.4118],
    "136. Daibo Pass 大望峠, Nagano": [36.7340, 137.9660],
    "137. Norikura Kogen 乗鞍高原, Nagano": [36.1205, 137.6310],
    "138. Shirouma Oike 白馬大池, Nagano": [36.8280, 137.7860],
    "139. Nojimazaki 野島崎, Chiba": [34.9013, 139.8882],
    "140. Kobentenjima 小弁天島, Chiba": [35.1134, 140.1988],
    "141. Izumo Hinomisaki 日御碕, Shimane": [35.4322, 132.6290],
    "142. Lake Shinji 宍道湖, Shimane": [35.4560, 132.9760],
    "143. Hashiguiiwa 橋杭岩, Wakayama": [33.4754, 135.7830],
    "144. Takeda Castle 竹田城跡, Hyogo": [35.3004, 134.8290],
    "145. Ine Funaya 伊根の舟屋, Kyoto": [35.6730, 135.2910],
    "146. Nima Sand Museum 仁摩サンドミュージアム, Shimane": [35.1230, 132.4940],
    "147. Shionomisaki Cape 潮岬, Wakayama": [33.4364, 135.7706],
    "148. Nariai-ji Temple 成相寺展望台, Kyoto": [35.5968, 135.2013],
    "149. Kumihama Bay 久美浜湾, Kyoto": [35.6180, 134.9030],
    "150. Kashiwajima 柏島, Kochi": [32.7492, 132.6278],
    "151. Tsunoshima Bridge 角島大橋, Yamaguchi": [34.3578, 130.8398],
    "152. Motonosumi Shrine 元乃隅神社, Yamaguchi": [34.3435, 131.0387],
    "153. Chichibugahama 父母ヶ浜, Kagawa": [34.2138, 133.6397],
    "154. Cape Muroto 室戸岬, Kochi": [33.2514, 134.1757],
    "155. Ouchi-juku 大内宿, Fukushima": [37.3384, 139.8478],
    "156. Hoshitoge Rice Terraces 星峠の棚田, Niigata": [37.0873, 138.6875],
    "157. Lake Hibara 桧原湖, Fukushima": [37.6902, 140.0605],
    "158. Cape Shiriya 尻屋崎, Aomori": [41.4295, 141.4726],
    "159. Lake Ogawara 小川原湖, Aomori": [40.8068, 141.2933],
    "160. Cape Nosappu 納沙布岬, Hokkaido": [43.3845, 145.8178],    
    "161. Cape Chikyu 地球岬, Hokkaido": [42.3158, 140.9803],
    "162. Lake Onneto オンネトー, Hokkaido": [43.2752, 143.3190],
    "163. Shirogane Blue Pond 青い池, Hokkaido": [43.4934, 142.6188],
    "164. Cape Esan 恵山岬, Hokkaido": [41.8065, 141.1667],
    "165. Koganezaki 黄金崎, Shizuoka": [34.7646, 138.7635],
    "166. Gokayama Ainokura 五箇山相倉集落, Toyama": [36.4259, 136.9357],
    "167. Mikuni Pass 三国峠, Hokkaido": [43.6408, 143.1754],
    "168. Oirase Stream 奥入瀬渓流, Aomori": [40.5228, 140.9344],
    "169. Tanesashi Coast 種差海岸, Aomori": [40.4746, 141.6047],
    "170. Kabushima Shrine 蕪島神社, Aomori": [40.5410, 141.5575],
    "171. Genbikei Gorge 厳美渓, Iwate": [38.9870, 141.1076],
    "172. Mt. Kurikoma 栗駒山, Miyagi": [38.9615, 140.7886],
    "173. Tengendai 天元台高原, Yamagata": [37.8820, 139.9940],
    "174. Bandai-san 磐梯山, Fukushima": [37.6008, 140.0722],
    "175. Akan International Crane 釧路湿原, Hokkaido": [43.0560, 144.2560],
    "176. Lake Akan 阿寒湖, Hokkaido": [43.4380, 144.0950],
    "177. Cape Ochiishi 落石岬, Hokkaido": [43.1700, 145.5100],
    "178. Lake Toya 洞爺湖, Hokkaido": [42.5970, 140.8540],
    "179. Noboribetsu Jigokudani 登別地獄谷, Hokkaido": [42.4940, 141.1510],
    "180. Muroto Geopark 室戸ジオパーク, Kochi": [33.3140, 134.1580],
    "181. Sadamisaki Peninsula 佐田岬, Ehime": [33.3440, 132.0230],
    "182. Mt. Ishizuchi 石鎚山, Ehime": [33.7650, 133.1180],
    "183. Iya Valley 祖谷のかずら橋, Tokushima": [33.8730, 133.8340],
    "184. Naruto Whirlpools 鳴門海峡, Tokushima": [34.2380, 134.6540],
    "185. Mt. Tsurugi 剣山, Tokushima": [33.8560, 134.0930],
    "186. Sandankyo Gorge 三段峡, Hiroshima": [34.6570, 132.2530],
    "187. Tomonoura 鞆の浦, Hiroshima": [34.3820, 133.3790],
    "188. Sandanbeki 三段壁, Wakayama": [33.6760, 135.3480],
    "189. Nachi Falls 那智の滝, Wakayama": [33.6750, 135.8920],
    "190. Koyasan 高野山奥之院, Wakayama": [34.2190, 135.5940],
    "191. Amanohashidate 天橋立, Kyoto": [35.5670, 135.1950],
    "192. Kinosaki Onsen 城崎温泉, Hyogo": [35.6320, 134.8080],
    "193. Hyonosen Ridge 氷ノ山, Hyogo": [35.3520, 134.4540],
    "194. Shodoshima Olive Park 小豆島, Kagawa": [34.4840, 134.2980],
    "195. Tsurugi Highlands 剣山スーパー林道, Tokushima": [33.8020, 134.0150],
    "196. Higashi-Aka Island 渡嘉敷島東阿嘉, Okinawa": [26.1860, 127.3520],
    "197. Shimanto River 四万十川, Kochi": [33.0030, 132.9340],
    "198. Cape Soya 宗谷岬, Hokkaido": [45.5215, 141.9367],
    "199. Kunimigaoka 国見ヶ丘, Miyazaki": [32.7510, 131.3300],
    "200. Kirishima Shrine 霧島神宮, Kagoshima": [31.8590, 130.8710],
    "201. Yakushima Shiratani 屋久島, Kagoshima": [30.3450, 130.5690],
    "202. Amami Oshima 奄美大島, Kagoshima": [28.3750, 129.4670],
    "203. Yonaguni Island 与那国島, Okinawa": [24.4500, 122.9800],
    "204. Iriomote Jungle カヌーツアー, Okinawa": [24.3500, 123.8500],
    "205. Okunoshima Rabbit 大久野島, Hiroshima": [34.3050, 132.9930],
    "206. Mitani Valley 三谷峡, Okayama": [34.8560, 133.7250],
    "207. Uradome Coast 浦富海岸, Tottori": [35.5880, 134.4600],
    "208. Izumo Taisha 出雲大社, Shimane": [35.4010, 132.6850],
    "209. Nita Pass 仁多峠, Shimane": [35.2610, 133.0840],
    "210. Oki Islands 隠岐の島, Shimane": [36.2160, 133.2330],
    "211. Dogo Islands 隠岐・島後, Shimane": [36.2500, 133.3000],
    "212. Ise Jingu 伊勢神宮, Mie": [34.4600, 136.7230],
    "213. Ryugadake Observatory 竜ヶ岳展望台, Yamanashi": [35.4561, 138.6102],
    "214. Gujo Hachiman 郡上八幡, Gifu": [35.7480, 136.9550],
    "215. Magome-juku 馬籠宿, Gifu": [35.4950, 137.5670],
    "216. Bessan Plateau 別山高原, Ishikawa": [36.0830, 136.7050],
    "217. Eiheiji Temple 永平寺, Fukui": [36.0540, 136.3570],
    "218. Tojinbo 東尋坊, Fukui": [36.2370, 136.1260],
    "219. Lake Biwa Biwako Terrace 琵琶湖, Shiga": [35.2090, 135.9180],
    "220. Mt. Ibuki Summit 伊吹山頂, Shiga": [35.4200, 136.4060],
    "221. Gozaisho Summit 御在所岳, Mie": [35.0120, 136.4380],
    "222. Iide Mountains 飯豊連峰, Yamagata": [37.8520, 139.7830],
    "223. Achi Village 阿智村 (日本一の星空), Nagano": [35.5180, 137.7280],
    "224. Dorokyo Gorge 瀞峡, Wakayama": [33.9070, 135.8500],
    "225. Awaji Southern Cape 淡路島南端, Hyogo": [34.2650, 134.8930],
    "226. Tottori Daisen 大山, Tottori": [35.3780, 133.5350],
    "227. Tsuno Plateau 津野山高原, Kochi": [33.4120, 133.0560],
    "228. Kawakami Village 川上村星空, Nara": [34.0560, 135.9740],
    "229. Miyajima 厳島神社, Hiroshima": [34.2970, 132.3190],
    "230. Kintaikyo Bridge 錦帯橋, Yamaguchi": [34.1670, 132.1790],
    "231. Kotohira-gu 金刀比羅宮, Kagawa": [34.1810, 133.8050],
    "232. Oboke Gorge 大歩危峡, Tokushima": [33.9120, 133.8420],
    "233. Daisetsuzan Asahidake 大雪山旭岳, Hokkaido": [43.6700, 142.8540],
    "234. Katsurahama Beach 桂浜, Kochi": [33.4980, 133.5710],
    "235. Hinokage Starfield 日之影星空, Miyazaki": [32.6290, 131.3870],
    "236. Sefuri Summit 脊振山頂, Fukuoka": [33.4280, 130.3060],
    "237. Sefuri Highlands 脊振山系, Saga": [33.3810, 130.1820],
    "238. Tara Highland 多良岳, Saga": [33.0610, 130.1700],
    "239. Unzen Nita Pass 雲仙仁田峠, Nagasaki": [32.7540, 130.2700],
    "240. Kuju Highlands 久住高原, Oita": [32.9880, 131.2400],
    "241. Ichifusa Highland 一房高原, Kumamoto": [32.3410, 130.9830],
    "242. Usuki Stone Buddhas 臼杵石仏, Oita": [33.0900, 131.7850],
    "243. Sakurajima East Coast 桜島有村溶岩展望所, Kagoshima": [31.5784, 130.6595],
    "244. Yanbaru Forest 与那覇岳, Okinawa": [26.7210, 128.2270],
    "245. Sefa-utaki 斎場御嶽, Okinawa": [26.1730, 127.8280],
    "246. Cape Manzamo 万座毛, Okinawa": [26.5040, 127.8500],
    "247. Aguni Island 粟国島, Okinawa": [26.5930, 127.2350],
    "248. Kume Island 久米島, Okinawa": [26.3390, 126.7860],
    "249. Zakimi Castle 座喜味城跡, Okinawa": [26.4110, 127.7420],
    "250. Cape Maeda 真栄田岬, Okinawa": [26.4460, 127.7800],

    # ── 251-266: 追加地点 ────────────────────────────────────────────────────────
    # Chiba
    "251. Isumi Railway Crossing いすみ鉄道第二五之町踏切, Chiba": [35.2827, 140.3465],
    "252. Oyama Senmaida 大山千枚田, Chiba": [35.2040, 140.1130],
    "253. Tonami no Torii 東浪見の鳥居, Chiba": [35.3541, 140.3842],
    # Toyama
    "254. Asahi Funakawa あさひ舟川「春の四重奏」, Toyama": [36.9610, 137.5580],
    # Ishikawa
    "255. Mawaki Ruins 真脇遺跡, Ishikawa": [37.2838, 137.1780],
    "256. Hoshi no Kanrankan 星の観察館, Ishikawa": [36.1880, 136.6680],
    "257. Hakusan Tenbodai 白山展望台, Ishikawa": [36.1350, 136.7720],
    # Fukushima
    "258. Shikanotsuno Observatory 鹿角平天文台, Fukushima": [37.1760, 140.3870],
    "259. Koriyama Nunobiki Wind Farm 郡山布引風の高原, Fukushima": [37.5064, 140.3260],
    "260. Bandaisan Viewpoint 磐梯山眺望箇所, Fukushima": [37.5680, 140.1360],
    "261. Kaneyama Fureai Hiroba かねやまふれあい広場, Fukushima": [37.4160, 139.5770],
    # Gunma
    "262. Ueno Sky Bridge 上野スカイブリッジ, Gunma": [36.1150, 138.8340],
    "263. Kurabuchi Children Observatory くらぶちこども天文台, Gunma": [36.5330, 138.9210],
    "264. Kozumaki Ranch Observatory 神津牧場天文台, Gunma": [36.3460, 138.8200],
    "265. Takane Observatory 高根展望台, Gunma": [36.5800, 139.0400],
    # Niigata
    "266. Okutadami Dam 奥只見ダム, Niigata": [37.0730, 139.1050],
    "267. Oshima Mihara-yama 三原山頂上, Tokyo": [34.7380, 139.3710],
    "268. Oshima Habu Port 波浮港, Tokyo": [34.6873, 139.4363],
    "269. Minami-Daito Island 南大東島, Okinawa": [25.8470, 131.2330],
}

st.set_page_config(page_title="Astro Map Pro", page_icon="🌌", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
<style>
    .block-container { padding-top: 0.8rem; padding-bottom: 0.8rem; padding-left: 2rem; padding-right: 2rem; }
    iframe { width: 100% !important; }
    .stTable table { width: 100% !important; margin-bottom: 0px !important; }
    .metric-card {
        background-color: #1e293b;
        padding: 15px;
        border-radius: 10px;
        border: 1px solid #334155;
        margin-bottom: 12px;
    }
    .source-card {
        background-color: #1e293b;
        border-radius: 10px;
        border: 1px solid #334155;
        margin-bottom: 12px;
        padding: 10px 15px 4px 15px;
    }
    .geo-highlight {
        font-family: 'Courier New', monospace;
        font-size: 19px;
        font-weight: bold;
        line-height: 1.6;
        margin-top: 5px;
    }
    .zenith-subtext {
        font-family: 'Courier New', monospace;
        font-size: 12px;
        color: #94a3b8;
        margin-top: 8px;
        border-top: 1px solid #475569;
        padding-top: 6px;
    }
    .footer-copyright {
        text-align: center; color: #64748b; font-size: 13px;
        font-weight: 500; margin-top: 30px; padding-top: 15px;
        border-top: 1px solid #334155;
    }
    /* Shrink gap between source label div and the selectbox below it */
    .source-card + div { margin-top: -10px !important; }
</style>
""", unsafe_allow_html=True)

# ── SESSION STATE ────────────────────────────────────────────────────────────
for k, v in [("lat", 35.6895), ("lon", 139.6917),
             ("map_center", [35.6895, 139.6917]), ("zoom", 7),
             ("day_offset", 0), ("location_name", "Tokyo, Japan"),
             ("is_custom_point", True), ("weather_source", "🔀 Blend (JMA+ECMWF+GFS)"),
             ("active_source_used", "JMA"),
             ("_last_tip", None), ("_last_lc", None),
             ("_source_auto", True), ("_ecmwf_available", True),
             ("map_tile", "windy"),
             ("_need_fly", False), ("_skip_prefetch", False),
             ("_scan_result", None)]:
    if k not in st.session_state:
        st.session_state[k] = v

# ── HELPERS ──────────────────────────────────────────────────────────────────
def _strip_loc_num(name: str) -> str:
    """Bỏ số thứ tự ở đầu tên địa danh: '15. Kamikochi...' → 'Kamikochi...'"""
    import re
    return re.sub(r'^\d+\.\s*', '', name).strip()

@st.cache_data(ttl=3600, show_spinner=False)   # cache 1 giờ — tên địa điểm không đổi
def fetch_location_name(lat, lon):
    url = f"https://nominatim.openstreetmap.org/reverse?format=json&lat={lat}&lon={lon}&zoom=10&addressdetails=1"
    try:
        res = requests.get(url, headers={"User-Agent": "AstroMapPro/7.0"}, timeout=3)
        if res.status_code == 200:
            addr = res.json().get("address", {})
            city = addr.get("city") or addr.get("town") or addr.get("village") or addr.get("county")
            state = addr.get("state")
            if city and state: return f"{city}, {state}"
            return state or city or "Unknown"
    except: pass
    return "Unknown Location"

def get_moon_phase_percent(date_obj):
    base = datetime(2024, 1, 11)
    phase = ((date_obj - base).total_seconds() / 86400.0 / 29.53059) % 1.0
    illum = round((1 - math.cos(phase * 2 * math.pi)) / 2 * 100, 1)
    if phase < 0.03 or phase > 0.97: desc = "New Moon（新月）🌑"
    elif phase < 0.22: desc = "Waxing Crescent（月齢初期）"
    elif phase < 0.28: desc = "First Quarter（上弦の月）"
    elif phase < 0.47: desc = "Waxing Gibbous（月齢中期）"
    elif phase < 0.53: desc = "Full Moon（満月）🌕"
    elif phase < 0.72: desc = "Waning Gibbous（月齢後期）"
    elif phase < 0.78: desc = "Last Quarter（下弦の月）"
    else: desc = "Waning Crescent（月齢末期）"
    return illum, desc

@st.cache_data(ttl=86400, show_spinner=False)  # cache 24 giờ — quỹ đạo trăng không đổi trong ngày
def calculate_exact_moon_altitude_ephem(lat, lon, year, month, day, hour_local, utc_offset_h=9.0):
    """Tính độ cao mặt trăng (có thể âm khi dưới đường chân trời).
    utc_offset_h là offset của location (JST=+9).
    Dùng +30 phút để tính giữa khung giờ → chính xác hơn khi hiển thị trên chart."""
    obs = ephem.Observer()
    obs.lat, obs.lon = str(lat), str(lon)
    obs.pressure = 0
    obs.epoch = ephem.J2000
    local_dt = datetime(year, month, day, hour_local, 30, 0)   # giữa giờ
    utc_dt   = local_dt - timedelta(hours=utc_offset_h)
    obs.date = ephem.Date(utc_dt)
    moon = ephem.Moon(); moon.compute(obs)
    return round(math.degrees(float(moon.alt)), 1)

@st.cache_data(ttl=86400, show_spinner=False)
def calculate_exact_sun_altitude_ephem(lat, lon, year, month, day, hour_local, utc_offset_h=9.0):
    """Tính độ cao mặt trời (có thể âm khi dưới đường chân trời = ban đêm).
    utc_offset_h là offset của location (JST=+9)."""
    obs = ephem.Observer()
    obs.lat, obs.lon = str(lat), str(lon)
    obs.pressure = 0
    obs.epoch = ephem.J2000
    local_dt = datetime(year, month, day, hour_local, 30, 0)   # giữa giờ
    utc_dt   = local_dt - timedelta(hours=utc_offset_h)
    obs.date = ephem.Date(utc_dt)
    sun = ephem.Sun(); sun.compute(obs)
    return round(math.degrees(float(sun.alt)), 1)

@st.cache_data(ttl=86400, show_spinner=False)
def calculate_milkyway_altitude(lat, lon, year, month, day, hour_local, utc_offset_h=9.0):
    """Tính độ cao trung tâm Dải Ngân Hà (Galactic Center, Sgr A*).
    RA = 17h45m40s, Dec = -29°00'28" (J2000)
    Trả về (altitude_deg, azimuth_deg) — altitude < 0 = dưới chân trời."""
    obs = ephem.Observer()
    obs.lat, obs.lon = str(lat), str(lon)
    obs.pressure = 0
    obs.epoch = ephem.J2000
    local_dt = datetime(year, month, day, hour_local, 30, 0)
    utc_dt   = local_dt - timedelta(hours=utc_offset_h)
    obs.date = ephem.Date(utc_dt)
    # Galactic Center: RA 17h45m40s, Dec -29°00'28" (J2000)
    gc = ephem.FixedBody()
    gc._ra  = ephem.hours('17:45:40.04')
    gc._dec = ephem.degrees('-29:00:28.1')
    gc._epoch = ephem.J2000
    gc.compute(obs)
    return round(math.degrees(float(gc.alt)), 1), round(math.degrees(float(gc.az)), 1)

def calculate_zenith_ra_dec(lat, lon):
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    d = (now - datetime(2000, 1, 1, 12, 0)).total_seconds() / 86400.0
    lst = (18.697374558 + 24.06570982441908 * d + lon / 15.0) % 24
    ra_h, ra_m = int(lst), int((lst % 1) * 60)
    dec_d, dec_m = int(lat), int((lat % 1) * 60)
    return f"{ra_h:02d}h {ra_m:02d}m", f"{dec_d:+03d}° {dec_m:02d}'"

def calculate_accurate_bortle(lat, lon):
    """Estimate Bortle class and SQM (mag/arcsec²) from coordinates.

    Methodology:
    ─────────────────────────────────────────────────
    Priority 1 — Per-location lookup table: values read directly from
      lightpollutionmap.info (VIIRS 2023 / Sky Brightness layer).
      If coordinates match within 5 km, use that value directly.

    Priority 2 — Geographic zone overrides (mountain/island/coastal zones
      calibrated from lightpollutionmap.info heatmap screenshots covering
      all of Japan from Hokkaido to Kyushu).

    Priority 3 — Weighted multi-city distance heuristic with per-city
      Bortle/SQM curves calibrated against ground-truth samples.

    Calibration sources (v5.17):
      · lightpollutionmap.info popup samples (page 15 of Japan_LPM.pdf):
          SQM 17.71 @ 35.69,139.71 (Tokyo core, Bortle 8-9)
          SQM 18.20 @ 35.54,139.69 (Kawasaki, Bortle 8-9)
          SQM 19.15 @ 35.27,139.67 (Yokohama suburb, Bortle 6)
          SQM 20.43 @ 36.23,137.96 (Nagano highlands elev 588m, Bortle 5)
          SQM 20.63 @ 35.13,139.61 (Boso coastal, Bortle 4)
          SQM 20.86 @ 35.14,139.19 (Sagami Bay coast, Bortle 4)
          SQM 21.62 @ 34.65,138.98 (Izu Peninsula, Bortle 4)
          SQM 21.62 @ 35.45,137.64 (Nagano elev 1172m, Bortle 4)
          SQM 21.77 @ 34.62,138.97 (Shimoda area, Bortle 3)
          SQM 21.94 @ 34.08,139.56 (Oshima Island, Bortle 2)
      · Heatmap visual analysis: pages 1-14 of Japan_LPM.pdf
          Full Japan overview + regional zoom (Kyushu, Kansai, Chubu,
          Kanto, Tohoku, Hokkaido) with coordinate overlays.

    Bortle ↔ SQM reference (Wikipedia / Bortle 2001 / Sky & Telescope):
      Class 1:   21.76–22.0    Class 2:   21.6–21.75
      Class 3:   21.3–21.6     Class 4:   20.8–21.3
      Class 4.5: 20.3–20.8     Class 5:   19.25–20.3
      Class 6:   18.5–19.25    Class 7:   18.0–18.5
      Class 8/9: < 18.0
    Source: lightpollutionmap.info · Falchi et al. 2016 · VIIRS 2023
    """
    # ── Lookup table: verified on lightpollutionmap.info VIIRS 2023 layer ───────
    # Color → Bortle mapping (lightpollutionmap.info standard palette):
    #   white/pink core → 9 | red → 8-9 | orange → 7-8 | yellow → 6-7
    #   yellow-green → 5-6 | light green → 4-5 | green → 4
    #   dark green → 3 | teal/blue-green → 2-3 | light blue → 2 | grey → 1
    _LOC_BORTLE = {
        # ── Kanagawa ──────────────────────────────────────────────────────────
        (35.1313, 139.6179): (4.5, 21.20), #  1 Jogashima          green     → Bortle 4 (20.8–21.3)
        (35.1408, 139.1609): (4.5, 20.80), #  6 Manazuru           light green (near Odawara) → 4.5 edge / 5
        (35.5400, 139.7030): (9, 17.80),   # Kawasaki city core    — lightpollutionmap SQM ≈17.8, Bortle 9
        (35.4437, 139.6380): (9, 17.90),   # Yokohama core         — very bright urban core
        # ── Chiba / Boso ──────────────────────────────────────────────────────
        (34.9517, 139.8103): (4, 21.20),   #  2 Tateyama           green
        (34.9071, 139.8611): (4, 21.20),   #  3 Minamiboso         green
        (35.1795, 140.3729): (4, 21.25),   #  4 Onjuku             green
        (35.3196, 140.4091): (4, 21.25),   #  5 Isumi              green
        # ── Shizuoka / Izu ────────────────────────────────────────────────────
        (34.6588, 138.9868): (3.5, 21.77), #  7 Shimoda — calibrated from sample SQM 21.77
        (34.6073, 138.8284): (3, 21.75),   #  8 Cape Aiai          dark green
        (34.7213, 138.7431): (3, 21.75),   #  9 Matsuzaki          dark green
        # ── Shizuoka inland ───────────────────────────────────────────────────
        (35.1704, 138.1811): (3, 21.75),   # 10 Okuoikojo          dark green
        (35.3832, 138.5836): (3, 21.75),   # 11 Asagiri Arena      dark green
        # ── Yamanashi ─────────────────────────────────────────────────────────
        (35.4912, 138.6049): (4, 21.70),   # 12 Shoji-ko           dark green (slight glow from Kofu)
        # ── Nagano ────────────────────────────────────────────────────────────
        (35.4457, 137.6617): (4, 21.62),   # 13 Hanamomo-no-sato   calibrated: SQM 21.62 → Class 3 (21.3–21.6 border)
        (35.8989, 137.4887): (3, 22.00),   # 14 Ontake             light blue (Japan Alps summit)
        (36.2502, 137.6392): (3, 22.00),   # 15 Kamikochi          light blue (deep Alps)
        (36.3991, 137.7151): (3, 21.95),   # 16 Enzan-so           light blue
        (36.2274, 138.1296): (3, 21.75),   # 17 Utsukushihara      dark green
        (36.1408, 138.3537): (3, 21.80),   # 18 JAXA               dark green
        # ── Gunma ─────────────────────────────────────────────────────────────
        (36.4773, 138.4646): (4, 21.75),   # 19 Tsumagoi           dark green
        (36.6534, 138.5274): (3, 21.80),   # 20 Yugama/Shibutoge   dark green
        (36.7325, 139.0601): (4, 21.30),   # 21 Sakura 上発知      green (Numata basin glow)
        # ── Tochigi ───────────────────────────────────────────────────────────
        (36.8036, 139.4236): (4, 21.75),   # 22 Oku-Nikko          dark green
        # ── Fukushima ─────────────────────────────────────────────────────────
        (37.3427, 140.6756): (3, 21.75),   # 23 Hoshinomura        dark green
        (37.7230, 140.2551): (3, 21.80),   # 24 Azuma-kofuji       dark green (volcanic plateau)
        # ── Miyagi ────────────────────────────────────────────────────────────
        (38.1361, 140.4468): (3, 21.75),   # 25 Okama 御釜         dark green
        # ── Ibaraki coast ─────────────────────────────────────────────────────
        (36.6144, 140.6802): (5, 20.80),   # 26 Higashinamekawa    light green (coastal urban) → 4.5/5
        # ── Tokyo ─────────────────────────────────────────────────────────────
        (35.7920, 139.0475): (5, 20.70),   # 27 Okutama            light green (Tokyo glow) → 4.5/5
        
        # ── Chiba ─────────────────────────────────────────────────────────────
        (35.7077, 140.8685): (4, 21.20),   # 28 Inubosaki
        (35.5307, 140.4428): (4.5, 21.00), # 29 Kujukuri
        (35.1604, 139.8357): (4.5, 21.00), # 30 Nokogiriyama
        # ── Ibaraki ───────────────────────────────────────────────────────────
        (36.3145, 140.5844): (5, 20.80),   # 31 Oarai
        (36.7657, 140.3542): (4, 21.40),   # 32 Fukuroda
        (36.6658, 140.4986): (4, 21.75),   # 33 Plateau Satomi
        # ── Gunma ─────────────────────────────────────────────────────────────
        (36.9306, 139.2150): (3, 21.90),   # 34 Oze
        (36.7833, 139.0830): (3.5, 21.60), # 35 Tanbara
        # ── Saitama ───────────────────────────────────────────────────────────
        (35.9563, 138.9255): (4, 21.40),   # 36 Misotsuchi
        (35.9977, 139.0124): (4, 21.40),   # 37 Nakatsu Gorge (replaced Mitsumine — too close to 36)
        # ── Tokyo Islands ─────────────────────────────────────────────────────
        (34.2086, 139.1358): (3, 21.80),   # 38 Kozushima
        (33.8740, 139.5950): (2.5, 21.95), # 39 Mikurajima
        (33.1003, 139.7706): (2.5, 21.95), # 40 Hachijojima
        (32.4666, 139.7678): (2, 22.00),   # 83 Aogashima
        (34.3872, 139.2878): (3, 21.80),   # 84 Niijima
        (34.3265, 139.2158): (3, 21.80),   # 85 Shikinejima
        (27.0944, 142.1917): (2, 22.00),   # 86 Ogasawara
        # ── Yamanashi ─────────────────────────────────────────────────────────
        (35.4154, 138.8758): (4, 21.50),   # 41 Yamanakako Panorama
        (35.8967, 138.4355): (3.5, 21.65), # 42 Kiyosato
        (35.5493, 138.7090): (4, 21.40),   # 43 Misaka Pass
        # ── Nagano ────────────────────────────────────────────────────────────
        (35.9405, 138.4740): (3, 21.80),   # 44 Nobeyama
        (36.1045, 138.0170): (4, 21.80),   # 45 Takabocchi
        (36.1030, 138.1946): (4, 21.75),   # 87 Kirigamine
        (36.1038, 138.1926): (4, 21.75),   # 88 Kurumayama
        (36.0690, 138.4567): (3, 21.80),   # 89 Yachiho
        (35.7725, 137.8173): (3, 21.90),   # 90 Senjojiki
        (36.6988, 137.8355): (3, 21.85),   # 91 Happo Pond
        (36.7582, 137.8758): (3, 21.85),   # 92 Tsugaike
        (36.7083, 137.8443): (3, 21.85),   # 93 Hakuba Iwatake
        (36.7172, 138.5177): (3, 21.80),   # 94 Shiga Highlands
        # ── Niigata ───────────────────────────────────────────────────────────
        (36.8917, 138.1708): (3, 21.75),   # 95 Myoko
        (37.7052, 138.8178): (4, 21.20),   # 96 Yahiko
        (38.2410, 139.4628): (4, 21.20),   # 97 Senami Coast
        # ── Yamagata ──────────────────────────────────────────────────────────
        (38.5484, 140.0264): (3, 21.85),   # 98 Gassan
        # ── Akita ─────────────────────────────────────────────────────────────
        (39.0933, 140.0497): (2.5, 21.90), # 99 Toriumi
        # ── Aomori ────────────────────────────────────────────────────────────
        (41.2570, 140.3495): (3, 21.75),   # 100 Cape Tappi
        # ── Gifu ──────────────────────────────────────────────────────────────
        (36.1068, 137.5538): (2.5, 21.95), # 47 Norikura
        (36.1658, 137.5507): (3, 21.90),   # 48 Hirayu
        (36.2898, 137.6462): (3, 21.90),   # 49 Shinhotaka
        # ── Ishikawa ──────────────────────────────────────────────────────────
        (36.2212, 136.7928): (3, 21.80),   # 50 Hakusan
        (36.8157, 136.7448): (4, 21.30),   # 51 Chirihama
        # ── Fukui ─────────────────────────────────────────────────────────────
        (35.5945, 135.8824): (4, 21.30),   # 52 Mikatagoko
        # ── Mie ───────────────────────────────────────────────────────────────
        (33.8930, 136.1113): (3, 21.80),   # 53 Oni-ga-jo
        (34.2708, 136.8964): (3.5, 21.60), # 54 Daiozaki
        # ── Nara ──────────────────────────────────────────────────────────────
        (34.5346, 136.1506): (3, 21.80),   # 46 Soni Highlands
        (34.1856, 136.1090): (2.5, 21.95), # 55 Odaigahara
        (34.2460, 135.8680): (3, 21.85),   # 56 Tenkawa
        # ── Hyogo ─────────────────────────────────────────────────────────────
        (35.0258, 134.3553): (2.5, 21.90), # 57 Nishiharima
        # ── Okayama ───────────────────────────────────────────────────────────
        (34.6712, 133.5483): (3, 21.80),   # 58 Bisei
        (35.2770, 133.6740): (3, 21.80),   # 59 Hiruzen
        # ── Tottori ───────────────────────────────────────────────────────────
        (35.5397, 134.2383): (3.5, 21.60), # 60 Tottori Sand Dunes
        (35.4087, 133.8618): (3.5, 21.60), # 61 Misasa
        # ── Yamaguchi ─────────────────────────────────────────────────────────
        (34.2576, 131.3070): (3, 21.80),   # 62 Akiyoshidai
        # ── Ehime ─────────────────────────────────────────────────────────────
        (33.3804, 132.9536): (2.5, 21.95), # 63 Shikoku Karst
        (33.4304, 132.1062): (3, 21.80),   # 65 Sata Cape
        # ── Kochi ─────────────────────────────────────────────────────────────
        (32.7196, 133.0182): (2.5, 21.95), # 64 Ashizuri
        # ── Saga ──────────────────────────────────────────────────────────────
        (33.5878, 129.8780): (3.5, 21.50), # 69 Yobuko
        # ── Nagasaki ──────────────────────────────────────────────────────────
        (33.3720, 129.3988): (3, 21.80),   # 68 Ikitsuki
        # ── Kumamoto ──────────────────────────────────────────────────────────
        (32.8845, 131.0808): (2.5, 21.95), # 66 Kusasenri
        (32.9506, 131.0904): (2.5, 21.95), # 67 Daikanbo
        # ── Miyazaki ──────────────────────────────────────────────────────────
        (32.7092, 131.3086): (3, 21.80),   # 70 Takachiho
        (31.3674, 131.3458): (2.5, 21.95), # 71 Cape Toi
        # ── Kagoshima ─────────────────────────────────────────────────────────
        (31.1805, 130.5284): (3, 21.80),   # 72 Kaimondake
        (27.0452, 128.4246): (2, 22.00),   # 73 Yoron
        # ── Okinawa ───────────────────────────────────────────────────────────
        (24.6053, 124.3427): (2, 22.00),   # 74 Hirakubozaki
        (24.4553, 124.2520): (2, 22.00),   # 75 Tamatorizaki
        (24.4078, 123.7575): (2, 22.00),   # 76 Iriomote
        (24.0558, 123.8060): (1.5, 22.00), # 77 Hateruma
        (26.4360, 127.7045): (3.5, 21.50), # 78 Cape Zanpa
        (26.7069, 128.0188): (3, 21.80),   # 79 Kouri Bridge
        (26.8716, 128.2695): (2.5, 21.95), # 80 Cape Hedo
        (24.7353, 125.4672): (2, 22.00),   # 81 Higashi-Hennazaki
        (24.7248, 125.2478): (2, 22.00),   # 82 Kurima Bridge

        # ── 101-174: Bổ sung ──────────────────────────────────────────────────
        (44.0174, 144.2740): (2.0, 22.00), # 101 Cape Notoro, Hokkaido
        (43.5763, 144.5360): (2.0, 22.00), # 102 Lake Mashu, Hokkaido
        (43.7398, 144.2570): (2.0, 22.00), # 103 Bihoro Pass, Hokkaido
        (43.6110, 144.3320): (2.0, 22.00), # 104 Lake Kussharo, Hokkaido
        (43.0808, 145.1174): (2.0, 22.00), # 105 Cape Kiritappu, Hokkaido
        (41.9272, 143.2473): (2.0, 22.00), # 106 Cape Erimo, Hokkaido
        (43.5765, 145.2765): (2.0, 22.00), # 107 Notsuke Peninsula, Hokkaido
        (44.1257, 143.9060): (2.0, 22.00), # 108 Lake Saroma, Hokkaido
        (44.0702, 145.1110): (2.0, 22.00), # 109 Shiretoko Pass, Hokkaido
        (43.3318, 140.3495): (2.5, 21.90), # 110 Cape Kamui, Hokkaido
        (41.5265, 140.9125): (2.5, 21.90), # 111 Omazaki, Aomori
        (41.3273, 140.8365): (2.5, 21.90), # 112 Hotokegaura, Aomori
        (40.4405, 140.8885): (2.5, 21.90), # 113 Lake Towada, Aomori
        (40.6530, 140.8770): (2.5, 21.90), # 114 Hakkoda, Aomori
        (39.7992, 140.8020): (2.5, 21.95), # 115 Nyuto Onsen, Akita
        (39.7264, 140.6954): (2.5, 21.95), # 116 Tazawako, Akita
        (39.9922, 139.7105): (2.5, 21.95), # 117 Oga Nyudozaki, Akita
        (39.6440, 141.9800): (3.0, 21.80), # 118 Jodogahama, Iwate
        (40.0715, 141.9472): (3.0, 21.80), # 119 Kitayamazaki, Iwate
        (39.8442, 141.8370): (3.0, 21.80), # 120 Ryusendo, Iwate
        (38.7480, 140.7190): (3.0, 21.80), # 121 Naruko Gorge, Miyagi
        (38.7350, 141.1030): (3.0, 21.70), # 122 Izunuma, Miyagi
        (38.7025, 139.9838): (3.0, 21.80), # 123 Mt. Haguro, Yamagata
        (38.6430, 140.5870): (3.0, 21.80), # 124 Funagata-yama, Miyagi
        (37.3445, 139.3150): (3.0, 21.80), # 125 Tadami Bridge, Fukushima
        (37.6550, 140.0720): (3.0, 21.75), # 126 Goshikinuma, Fukushima
        (37.5460, 140.1040): (3.0, 21.75), # 127 Inawashiro Lake, Fukushima
        (36.8174, 137.0452): (3.5, 21.50), # 128 Amaharashi Coast, Toyama
        (36.5776, 137.6064): (2.5, 21.95), # 129 Tateyama Murodo, Toyama
        (36.5860, 136.9710): (3.0, 21.80), # 130 Shogawa Gorge, Toyama
        (37.3961, 137.2474): (3.0, 21.80), # 131 Mitsukejima, Ishikawa
        (37.4252, 136.9996): (3.0, 21.80), # 132 Senmaida, Ishikawa
        (37.5289, 137.3261): (3.0, 21.80), # 133 Rokkozaki, Ishikawa
        (36.1560, 136.7490): (2.5, 21.95), # 134 Hakusan Chokaisanso, Ishikawa
        (35.4859, 137.4118): (3.5, 21.60), # 135 Ena Ravine, Gifu
        (36.7340, 137.9660): (3.0, 21.85), # 136 Daibo Pass, Nagano
        (36.1205, 137.6310): (2.5, 21.95), # 137 Norikura Kogen, Nagano
        (36.8280, 137.7860): (3.0, 21.90), # 138 Shirouma Oike, Nagano
        (34.9013, 139.8882): (4.0, 21.20), # 139 Nojimazaki, Chiba
        (35.1134, 140.1988): (4.0, 21.20), # 140 Kobentenjima, Chiba
        (35.4322, 132.6290): (3.0, 21.80), # 141 Izumo Hinomisaki, Shimane
        (35.4560, 132.9760): (3.0, 21.75), # 142 Lake Shinji, Shimane
        (35.1230, 132.4940): (3.0, 21.80), # 146 Nima Sand Museum, Shimane
        (33.4754, 135.7830): (3.0, 21.80), # 143 Hashiguiiwa, Wakayama
        (33.4364, 135.7706): (3.0, 21.80), # 147 Shionomisaki Cape, Wakayama
        (35.3004, 134.8290): (3.0, 21.80), # 144 Takeda Castle, Hyogo
        (35.6730, 135.2910): (3.5, 21.60), # 145 Ine Funaya, Kyoto
        (35.5968, 135.2013): (3.0, 21.75), # 148 Nariai-ji, Kyoto
        (35.6180, 134.9030): (3.0, 21.70), # 149 Kumihama Bay, Kyoto
        (32.7492, 132.6278): (2.5, 21.95), # 150 Kashiwajima, Kochi
        (34.3578, 130.8398): (3.0, 21.80), # 151 Tsunoshima Bridge, Yamaguchi
        (34.3435, 131.0387): (3.0, 21.80), # 152 Motonosumi Shrine, Yamaguchi
        (34.2138, 133.6397): (3.5, 21.50), # 153 Chichibugahama, Kagawa
        (33.2514, 134.1757): (2.5, 21.95), # 154 Cape Muroto, Kochi
        (37.3384, 139.8478): (3.0, 21.75), # 155 Ouchi-juku, Fukushima
        (37.0873, 138.6875): (3.0, 21.80), # 156 Hoshitoge, Niigata
        (37.6902, 140.0605): (3.0, 21.75), # 157 Lake Hibara, Fukushima
        (41.4295, 141.4726): (2.5, 21.90), # 158 Cape Shiriya, Aomori
        (40.8068, 141.2933): (3.0, 21.75), # 159 Lake Ogawara, Aomori
        (43.3845, 145.8178): (2.0, 22.00), # 160 Cape Nosappu, Hokkaido
        (42.3158, 140.9803): (2.5, 21.90), # 161 Cape Chikyu, Hokkaido
        (43.2752, 143.3190): (2.0, 22.00), # 162 Lake Onneto, Hokkaido
        (43.4934, 142.6188): (2.0, 22.00), # 163 Shirogane Blue Pond, Hokkaido
        (41.8065, 141.1667): (2.5, 21.90), # 164 Cape Esan, Hokkaido
        (34.7646, 138.7635): (3.0, 21.80), # 165 Koganezaki, Shizuoka
        (36.4259, 136.9357): (3.0, 21.80), # 166 Gokayama, Toyama
        (43.6408, 143.1754): (2.0, 22.00), # 167 Mikuni Pass, Hokkaido
        (40.5228, 140.9344): (2.5, 21.90), # 168 Oirase Stream, Aomori
        (40.4746, 141.6047): (3.0, 21.80), # 169 Tanesashi Coast, Aomori
        (40.5410, 141.5575): (3.0, 21.80), # 170 Kabushima Shrine, Aomori
        (38.9870, 141.1076): (3.0, 21.80), # 171 Genbikei Gorge, Iwate
        (38.9615, 140.7886): (3.0, 21.80), # 172 Mt. Kurikoma, Miyagi
        (37.8820, 139.9940): (3.0, 21.80), # 173 Tengendai, Yamagata
        (37.6008, 140.0722): (3.0, 21.75), # 174 Bandai-san, Fukushima
        
        # ── 175-250: Dữ liệu Bortle và SQM bổ sung ────────────────────────────
        (43.0560, 144.2560): (2.0, 21.80), # 175 Akan Intl Crane Center
        (43.4380, 144.0950): (2.5, 21.70), # 176 Lake Akan
        (43.1700, 145.5100): (2.0, 21.85), # 177 Cape Ochiishi
        (42.5970, 140.8540): (3.0, 21.50), # 178 Lake Toya
        (42.4940, 141.1510): (3.0, 21.45), # 179 Noboribetsu Jigokudani
        (33.3140, 134.1580): (2.5, 21.90), # 180 Muroto Geopark, Kochi
        (33.3440, 132.0230): (2.5, 21.65), # 181 Sadamisaki Peninsula
        (33.7650, 133.1180): (2.0, 21.80), # 182 Mt. Ishizuchi
        (33.8730, 133.8340): (2.5, 21.60), # 183 Iya Valley
        (33.9120, 133.8420): (3.0, 21.70), # 232 Oboke Gorge, Tokushima
        (34.2380, 134.6540): (3.5, 21.20), # 184 Naruto Whirlpools
        (33.8560, 134.0930): (2.0, 21.75), # 185 Mt. Tsurugi
        (34.6570, 132.2530): (3.0, 21.40), # 186 Sandankyo Gorge
        (34.3820, 133.3790): (3.5, 21.10), # 187 Tomonoura
        (33.6760, 135.3480): (3.0, 21.50), # 188 Sandanbeki
        (33.6750, 135.8920): (2.5, 21.60), # 189 Nachi Falls
        (34.2190, 135.5940): (2.5, 21.65), # 190 Koyasan
        (35.5670, 135.1950): (3.5, 21.10), # 191 Amanohashidate
        (35.6320, 134.8080): (3.0, 21.30), # 192 Kinosaki Onsen
        (35.3520, 134.4540): (2.5, 21.80), # 193 Hyonosen Ridge, Hyogo (1510m, deep mountains)
        (34.4840, 134.2980): (3.0, 21.20), # 194 Shodoshima Olive Park
        (33.8020, 134.0150): (2.0, 21.85), # 195 Tsurugi Super Rindo, Tokushima (highland forest road)
        (26.1860, 127.3520): (3.0, 21.70), # 196 Higashi-Aka Island, Kerama (remote island)
        (33.0030, 132.9340): (2.0, 21.80), # 197 Shimanto River
        (45.5215, 141.9367): (2.0, 21.95), # 198 Cape Soya, Hokkaido (northernmost tip, remote)
        (32.7510, 131.3300): (2.5, 21.70), # 199 Kunimigaoka, Miyazaki
        (31.8590, 130.8710): (2.5, 21.65), # 200 Kirishima Shrine
        (30.3450, 130.5690): (2.0, 21.80), # 201 Yakushima
        (28.3750, 129.4670): (2.5, 21.60), # 202 Amami Oshima
        (24.4500, 122.9800): (1.5, 22.00), # 203 Yonaguni Island, Okinawa (westernmost Japan, near-pristine)
        (24.3500, 123.8500): (2.0, 21.85), # 204 Iriomote Jungle
        (34.3050, 132.9930): (3.5, 21.10), # 205 Okunoshima
        (34.8560, 133.7250): (2.5, 21.60), # 206 Mitani Valley
        (35.5880, 134.4600): (3.0, 21.80), # 207 Uradome Coast, Tottori
        (35.4010, 132.6850): (3.0, 21.30), # 208 Izumo Taisha
        (35.2610, 133.0840): (2.5, 21.75), # 209 Nita Pass, Shimane (Chugoku mountains)
        (36.2160, 133.2330): (2.0, 21.75), # 210 Oki Islands
        (36.2500, 133.3000): (2.0, 21.75), # 211 Dogo Islands
        (34.4600, 136.7230): (3.5, 21.00), # 212 Ise Jingu
        (35.4561, 138.6102): (2.0, 22.00), # 213 Ryugadake Observatory, Yamanashi (1485m, near Shoji-ko)
        (35.7480, 136.9550): (3.0, 21.40), # 214 Gujo Hachiman
        (35.4950, 137.5670): (3.0, 21.30), # 215 Magome-juku
        (36.0830, 136.7050): (2.5, 21.85), # 216 Bessan Plateau, Ishikawa (Hakusan foothills)
        (36.0540, 136.3570): (3.0, 21.40), # 217 Eiheiji Temple
        (36.2370, 136.1260): (3.0, 21.40), # 218 Tojinbo
        (35.2090, 135.9180): (3.0, 21.40), # 219 Lake Biwa Terrace
        (35.4200, 136.4060): (3.0, 21.60), # 220 Mt. Ibuki Summit, Shiga (1377m)
        (35.0120, 136.4380): (3.0, 21.55), # 221 Gozaisho Summit, Mie (1212m, Suzuka range)
        (37.8520, 139.7830): (2.0, 21.95), # 222 Iide Mountains, Yamagata (deep Tohoku mountains)
        (35.5180, 137.7280): (2.0, 21.95), # 223 Achi Village, Nagano (Japan's "starriest sky")
        (33.9070, 135.8500): (2.5, 21.85), # 224 Dorokyo Gorge, Wakayama
        (34.2650, 134.8930): (3.5, 21.40), # 225 Awaji Southern Cape, Hyogo (away from Kobe/Osaka)
        (35.3780, 133.5350): (2.5, 21.60), # 226 Tottori Daisen
        (33.4120, 133.0560): (2.0, 21.90), # 227 Tsuno Plateau, Kochi (Shikoku highlands)
        (34.0560, 135.9740): (2.5, 21.85), # 228 Kawakami Village, Nara (deep Yoshino mountains)
        (34.2970, 132.3190): (3.5, 21.00), # 229 Miyajima
        (34.1670, 132.1790): (3.5, 21.10), # 230 Kintaikyo Bridge
        (34.1810, 133.8050): (3.0, 21.40), # 231 Kotohira-gu
        (33.8730, 133.8340): (2.5, 21.60), # 232 Iya Kazurabashi
        (43.6700, 142.8540): (2.0, 21.90), # 233 Daisetsuzan Asahidake, Hokkaido (1600m+, remote highland)
        (33.4980, 133.5710): (3.5, 21.10), # 234 Katsurahama Beach
        (32.6290, 131.3870): (2.0, 21.95), # 235 Hinokage Starfield, Miyazaki (Kyushu deep mountains)
        (33.4280, 130.3060): (3.0, 21.60), # 236 Sefuri Summit, Fukuoka (1054m, JAXA station nearby)
        (33.3810, 130.1820): (2.5, 21.85), # 237 Sefuri Highlands, Saga (deep mountain range)
        (33.0610, 130.1700): (2.5, 21.80), # 238 Tara Highland, Saga (remote mountain)
        (32.7540, 130.2700): (2.5, 21.80), # 239 Unzen Nita Pass, Nagasaki (1080m, national park)
        (32.9880, 131.2400): (2.5, 21.90), # 240 Kuju Highlands, Oita
        (32.3410, 130.9830): (2.5, 21.85), # 241 Ichifusa Highland, Kumamoto (deep Kyushu mountains)
        (33.0900, 131.7850): (3.0, 21.30), # 242 Usuki Stone Buddhas
        (31.5784, 130.6595): (3.5, 21.20), # 243 Sakurajima East Coast (有村溶岩, away from Kagoshima)
        (26.7210, 128.2270): (3.0, 21.70), # 244 Yanbaru Forest, Okinawa (UNESCO natural heritage, north Okinawa)
        (26.1730, 127.8280): (3.0, 21.30), # 245 Sefa-utaki
        (26.5040, 127.8500): (3.0, 21.30), # 246 Cape Manzamo
        (26.5930, 127.2350): (2.0, 22.00), # 247 Aguni Island, Okinawa (tiny remote island, Bortle 2)
        (26.3390, 126.7860): (2.0, 21.95), # 248 Kume Island, Okinawa (remote island, dark skies)
        (26.4110, 127.7420): (3.5, 21.10), # 249 Zakimi Castle
        (26.4460, 127.7800): (3.0, 21.30), # 250 Cape Maeda

        # ── 251-266: 追加地点 ──────────────────────────────────────────────────────
        (35.2827, 140.3465): (4.0, 21.20), # 251 Isumi Railway Crossing, Chiba
        (35.2040, 140.1130): (4.5, 21.00), # 252 Oyama Senmaida, Chiba
        (35.3541, 140.3842): (4.0, 21.20), # 253 Tonami no Torii, Chiba
        (36.9610, 137.5580): (3.0, 21.80), # 254 Asahi Funakawa, Toyama
        (37.2838, 137.1780): (3.0, 21.75), # 255 Mawaki Ruins, Ishikawa
        (36.1880, 136.6680): (3.0, 21.80), # 256 Hoshi no Kanrankan, Ishikawa
        (36.1350, 136.7720): (3.0, 21.80), # 257 Hakusan Tenbodai, Ishikawa
        (37.1760, 140.3870): (3.0, 21.80), # 258 Shikanotsuno Observatory, Fukushima
        (37.5064, 140.3260): (3.5, 21.60), # 259 Koriyama Nunobiki, Fukushima
        (37.5680, 140.1360): (3.0, 21.75), # 260 Bandaisan Viewpoint, Fukushima
        (37.4160, 139.5770): (3.0, 21.80), # 261 Kaneyama Fureai, Fukushima
        (36.1150, 138.8340): (4.0, 21.30), # 262 Ueno Sky Bridge, Gunma
        (36.5330, 138.9210): (3.5, 21.60), # 263 Kurabuchi Observatory, Gunma
        (36.3460, 138.8200): (3.5, 21.60), # 264 Kozumaki Ranch, Gunma
        (36.5800, 139.0400): (3.5, 21.60), # 265 Takane Observatory, Gunma
        (37.0730, 139.1050): (2.5, 21.90), # 266 Okutadami Dam, Niigata
        (34.7380, 139.3710): (2.0, 22.00), # 267 Oshima Mihara-yama summit (758m, Izu Oshima)
        (34.6873, 139.4363): (2.0, 21.95), # 268 Oshima Habu Port (south, away from Motomachi)
        (25.8470, 131.2330): (1.5, 22.05), # 269 Minami-Daito Island, Okinawa (remote Pacific island, pristine sky)
    }

    def _km(la1, lo1, la2, lo2):
        dlat = (la1 - la2) * 111.0
        dlon = (lo1 - lo2) * 111.0 * math.cos(math.radians((la1 + la2) / 2))
        return math.sqrt(dlat**2 + dlon**2)

    # Priority 1: exact location match within 5 km
    for (plat, plon), (bc, sq) in _LOC_BORTLE.items():
        if _km(lat, lon, plat, plon) < 5.0:
            return bc, sq

    # ── Priority 2: Geographic zone overrides ────────────────────────────────
    # Calibrated from heatmap analysis of Japan_LPM.pdf pages 1-14.
    # Zones listed from darkest (highest priority) to brightest.

    # Japan Alps core — Bortle 1-2 (grey/light-blue on heatmap)
    # Covers: Kamikochi, Hotaka, Yari, Tateyama, Hakuba deep valleys
    if 36.0 < lat < 36.8 and 137.3 < lon < 137.9:
        return 2, 21.95

    # Northern Japan Alps / Ontake / Norikura area
    if 35.7 < lat < 36.2 and 137.2 < lon < 137.7:
        return 2, 22.00

    # Southern Alps (Minami Alps / Akaishi) — Bortle 2-3
    if 35.3 < lat < 35.8 and 137.5 < lon < 138.1:
        return 2, 22.00

    # Shizuoka deep mountain interior (Okuoi / Ikawa)
    if 35.0 < lat < 35.4 and 137.8 < lon < 138.3:
        return 3, 21.80

    # Asagiri Plateau / Fuji Highland area
    if 35.28 < lat < 35.48 and 138.45 < lon < 138.70:
        return 3, 21.75

    # Izu Peninsula tip (south of Shimoda) — dark green
    if lat < 34.72 and 138.70 < lon < 139.10:
        return 3, 21.80

    # Izu Oshima / Izu Islands — Bortle 2 (nearly pitch black, calibrated SQM 21.94)
    if 33.8 < lat < 34.8 and 139.3 < lon < 139.8 and _km(lat, lon, 34.08, 139.56) < 20:
        return 2, 21.94

    # Ogasawara / Bonin Islands — Bortle 1 (extreme remote)
    if lat < 28.0 and 141.0 < lon < 143.0:
        return 1, 22.20

    # Nikko highlands / Oku-Nikko (Yunoko, Senjogahara)
    if 36.70 < lat < 36.90 and 139.35 < lon < 139.60:
        return 3, 21.75

    # Oku-Chichibu mountains (Gunma/Saitama/Yamanashi border)
    if 35.8 < lat < 36.2 and 138.6 < lon < 139.2 and _km(lat, lon, 35.97, 138.87) > 20:
        return 3, 21.75

    # Noto Peninsula tip — Bortle 3 (light blue on heatmap)
    if 37.2 < lat < 37.6 and 136.8 < lon < 137.4:
        return 3, 21.80

    # Tohoku highlands / Ou Mountains core
    if 37.5 < lat < 40.5 and 140.2 < lon < 141.0 and _km(lat, lon, 38.27, 140.87) > 30:
        return 3, 21.75

    # Azuma/Adatara volcanic plateau (Fukushima)
    if 37.60 < lat < 37.90 and 140.1 < lon < 140.4:
        return 3, 21.80

    # Sanriku coast (Iwate/Miyagi) — relatively dark coastal
    if 38.5 < lat < 40.5 and 141.3 < lon < 142.0:
        return 4, 21.30

    # Akita / Yamagata highlands — Bortle 3-4
    if 38.5 < lat < 40.5 and 140.0 < lon < 140.8 and _km(lat, lon, 39.72, 140.10) > 20:
        return 3, 21.75

    # Hokkaido — Daisetsuzan / Shiretoko core (nearly pitch black)
    if 43.3 < lat < 44.0 and 142.5 < lon < 144.5:
        return 2, 22.00

    # Hokkaido interior mountains (away from Sapporo/Asahikawa)
    if 42.5 < lat < 45.5 and 141.5 < lon < 144.5 and _km(lat, lon, 43.06, 141.35) > 40 and _km(lat, lon, 43.77, 142.37) > 25:
        return 3, 21.75

    # Eastern Hokkaido (Kushiro/Abashiri area) — Bortle 4
    if 43.0 < lat < 44.5 and 144.0 < lon < 145.5:
        return 4, 21.30

    # Kyushu highlands (Aso / Kuju / Kirishima) — Bortle 3
    if 32.5 < lat < 33.2 and 130.8 < lon < 131.4:
        return 3, 21.75

    # Miyazaki coast / Nichinan — Bortle 4 (light green on heatmap)
    if 31.3 < lat < 32.2 and 131.2 < lon < 131.8:
        return 4, 21.20

    # Kagoshima south (Satsuma Peninsula tip) — Bortle 4
    if lat < 31.5 and 130.4 < lon < 130.8:
        return 4, 21.20

    # Amami / Okinawa islands — Bortle 3-4 (remote, minimal pollution)
    if lat < 28.5 and 127.0 < lon < 131.0:
        return 3, 21.80

    # Shikoku mountains (Kochi interior) — Bortle 3
    if 33.4 < lat < 33.9 and 133.0 < lon < 133.8:
        return 3, 21.75

    # Sea of Japan coastal Tohoku / Akita — Bortle 4
    if 38.0 < lat < 40.5 and 139.0 < lon < 140.2 and _km(lat, lon, 39.72, 140.10) > 15:
        return 4, 21.30

    # ── Priority 3: Min-distance heuristic (approach from v5.10, extended to all Japan)
    # Concept: inspired by v5.10's simple min-distance threshold approach.
    # Each city has a center SQM (calibrated from lightpollutionmap.info).
    # SQM recovers with distance via a universal delta table.
    # Final SQM = min across all cities (most polluted city wins).
    # Validated against 10 ground-truth samples from Japan_LPM.pdf — all within ±1 Bortle class.
    #
    # Delta table (km from city center → SQM added to city's center_sqm):
    #   ≤4km:+0.0  ≤8km:+0.3  ≤15km:+0.7  ≤25km:+1.2  ≤40km:+1.8
    #   ≤65km:+2.5  ≤100km:+3.2  ≤150km:+3.7  >150km:+4.0
    # Calibration: Tokyo(0km)=17.50 → Machida(27km)=18.81 [delta≈1.3, matches ≤25 band]
    #              Yokohama(0km)=17.80 → Yokosuka(35km)=19.15 [delta≈1.35, matches ≤40 band]
    _DELTA_BANDS = [
        (4,   0.0),
        (8,   0.3),
        (15,  0.7),
        (25,  1.2),
        (40,  1.8),
        (65,  2.5),
        (100, 3.2),
        (150, 3.7),
    ]
    def _get_delta(d):
        for _thresh, _delta in _DELTA_BANDS:
            if d <= _thresh:
                return _delta
        return 4.0  # > 150km → negligible

    # (lat, lon, name, center_sqm) — center_sqm calibrated from lightpollutionmap.info
    _CITIES = [
        # ── Kanto mega-region ──────────────────────────────────────────────────
        (35.6895, 139.6917, "Tokyo",       17.40),
        (35.4437, 139.6380, "Yokohama",    17.60),
        (35.5400, 139.7030, "Kawasaki",    17.60),  # calibrated SQM 18.20 @ 10km
        (35.8616, 139.6455, "Saitama",     18.20),
        (35.6074, 140.1063, "Chiba",       18.20),        # Kanto suburban dense ring — critical for Setagaya/Noborito/Machida accuracy
        (35.6430, 139.6529, "Setagaya",    17.90),  # inner Tokyo ward, between Tokyo & Kawasaki
        (35.5503, 139.5491, "Tama-Plaza",  18.50),  # Kawasaki Aoba-ku
        (35.5480, 139.4454, "Machida",     18.60),  # calibrated from PDF SQM 18.81 nearby
        (35.6993, 139.4107, "Tachikawa",   18.60),
        (35.6598, 139.3188, "Hachioji",    18.60),
        (35.4385, 139.3653, "Atsugi",      18.60),
        (35.9264, 139.4841, "Kawagoe",     19.10),
        (35.2815, 139.6695, "Yokosuka",    19.10),
        (35.2700, 139.6700, "Yokohama-S",  18.25),  # calibrated SQM 19.15 (Totsuka/Yokosuka)
        (35.6562, 138.5692, "Kofu",        19.80),
        (35.2682, 139.1634, "Odawara",     19.75),
        (36.3278, 139.0110, "Takasaki",    19.50),
        # ── Kansai mega-region ─────────────────────────────────────────────────
        (34.6937, 135.5023, "Osaka",       17.60),
        (34.6843, 135.8068, "Nara",        19.20),
        (34.6901, 135.1956, "Kobe",        18.50),
        (35.0116, 135.7681, "Kyoto",       18.70),
        (35.1815, 136.9066, "Nagoya",      17.80),
        # ── Other major cities ─────────────────────────────────────────────────
        (34.7650, 137.3923, "Toyohashi",   19.40),
        (35.4128, 136.7586, "Gifu",        19.30),        
        (43.0621, 141.3544, "Sapporo",     18.50),
        (33.5904, 130.4017, "Fukuoka",     18.50),
        (33.8834, 130.8751, "Kitakyushu",  18.80),
        (38.2682, 140.8694, "Sendai",      19.20),
        (34.6567, 133.9207, "Okayama",     19.20),
        (34.4875, 133.3742, "Fukuyama",    19.70),
        (34.3853, 132.4553, "Hiroshima",   19.20),
        (34.8152, 134.6812, "Himeji",      19.30),
        (34.3380, 134.0495, "Takamatsu",   19.60),
        (34.6551, 133.9195, "Okayama",     19.80),
        (43.7706, 142.3650, "Asahikawa",   20.30),
        (37.9161, 139.0364, "Niigata",     19.50),
        (36.5613, 136.6562, "Kanazawa",    19.40),
        (36.6953, 137.2113, "Toyama",      19.50),
        (36.6485, 138.1949, "Nagano",      20.05),
        (36.0627, 136.2177, "Fukui",       19.65),
        (34.9769, 138.3831, "Shizuoka",    19.40),
        (34.7108, 137.7262, "Hamamatsu",   19.10),
        (36.2380, 137.9720, "Matsumoto",   20.43),  # calibrated SQM 20.43
        (32.7898, 130.7417, "Kumamoto",    19.50),
        (31.5966, 130.5571, "Kagoshima",   19.50),
        (33.8395, 132.7657, "Matsuyama",   20.10),
        (33.2375, 131.6101, "Oita",        19.40),
        (34.0657, 134.5590, "Tokushima",   20.30),
        (34.3400, 134.0434, "Takamatsu",   20.30),
        (33.5597, 133.5311, "Kochi-c",     20.30),
        (36.3898, 139.0634, "Maebashi",    19.50),
        (36.5550, 139.8829, "Utsunomiya",  19.50),
        (37.3983, 140.3870, "Koriyama",    19.50),
        (37.7500, 140.4677, "Fukushima-c", 20.10),
        (39.7186, 140.1023, "Akita-c",     20.10),
        (40.8244, 140.7400, "Aomori-c",    20.30),
        (26.2124, 127.6792, "Naha",        19.50),
        
        # ── Hokkaido ──────────────────────────────────────────────────────────
        (42.9849, 144.3814, "Kushiro",      20.40),
        (44.0206, 144.2730, "Abashiri",     20.60),
        (45.4156, 141.6731, "Wakkanai",     20.80),
        (42.3172, 140.9738, "Muroran",      19.60),
        (42.5510, 141.3550, "Tomakomai",    19.40),
        (42.9238, 143.1968, "Obihiro",      20.20),
        (43.8031, 143.8958, "Kitami",       20.40),
        (41.7687, 140.7288, "Hakodate",     19.60),

        # ── Tohoku ────────────────────────────────────────────────────────────
        (40.5123, 141.4880, "Hachinohe",    19.90),
        (39.7036, 141.1527, "Morioka",      20.10),
        (39.6411, 141.9571, "Miyako",       20.50),
        (39.3150, 141.1167, "Hanamaki",     20.20),
        (38.2554, 140.8777, "Natori",       19.40),
        (38.4342, 141.3028, "Ishinomaki",   19.80),
        (38.9081, 139.8365, "Sakata",       20.20),
        (38.9140, 139.8500, "Tsuruoka",     20.20),
        (37.4947, 139.9297, "Aizuwakamatsu",20.30),
        (37.0505, 140.8877, "Iwaki",        19.70),

        # ── Ibaraki ───────────────────────────────────────────────────────────
        (36.3418, 140.4468, "Mito",         19.50),
        (36.0835, 140.0764, "Tsukuba",      19.20),
        (36.3966, 140.5348, "Hitachi",      19.50),
        (35.9654, 140.6448, "Kashima",      19.60),
        (36.1812, 139.9930, "Koga",         19.30),

        # ── Tochigi ───────────────────────────────────────────────────────────
        (36.5658, 139.8836, "Kanuma",       19.70),
        (36.8717, 139.9959, "Nasu-Shiobara",20.10),
        (36.3140, 139.8000, "Oyama",        19.30),

        # ── Gunma ─────────────────────────────────────────────────────────────
        (36.3219, 139.0033, "Isesaki",      19.30),
        (36.2916, 139.3753, "Ota",          19.20),
        (36.3380, 139.1970, "Kiryu",        19.60),

        # ── Saitama ───────────────────────────────────────────────────────────
        (35.9756, 139.7528, "Kasukabe",     18.80),
        (35.8303, 139.8057, "Koshigaya",    18.60),
        (35.9917, 139.0858, "Chichibu",     20.30),
        (35.8569, 139.6489, "Kawaguchi",    18.20),

        # ── Chiba ─────────────────────────────────────────────────────────────
        (35.7345, 140.8266, "Choshi",       19.60),
        (35.6047, 140.1233, "Funabashi",    18.10),
        (35.7876, 140.3186, "Narita",       19.10),
        (35.7204, 140.1024, "Matsudo",      18.20),
        (35.4979, 140.1141, "Ichihara",     18.70),

        # ── Tokyo Metro ───────────────────────────────────────────────────────
        (35.7289, 139.7100, "Ikebukuro",    17.30),
        (35.6938, 139.7034, "Shinjuku",     17.20),
        (35.6580, 139.7016, "Shibuya",      17.20),
        (35.7138, 139.7772, "Ueno",         17.40),
        (35.6812, 139.7671, "Tokyo-Sta",    17.20),

        # ── Kanagawa ──────────────────────────────────────────────────────────
        (35.3358, 139.3496, "Hiratsuka",    18.90),
        (35.3192, 139.5467, "Kamakura",     19.10),
        (35.2646, 139.1521, "Hakone",       20.30),
        (35.2836, 139.6722, "Miura",        19.40),

        # ── Yamanashi ─────────────────────────────────────────────────────────
        (35.6639, 138.5684, "Kai",          19.80),
        (35.4875, 138.8078, "Fujiyoshida",  20.20),
        (35.5500, 138.9000, "Yamanakako",   20.60),

        # ── Nagano ────────────────────────────────────────────────────────────
        (36.6513, 138.1810, "Suzaka",       20.20),
        (36.3134, 138.5968, "Saku",         20.60),
        (36.2140, 138.2520, "Komoro",       20.50),
        (35.5147, 137.8218, "Iida",         20.30),
        (35.7286, 137.9537, "Ina",          20.40),

        # ── Niigata ───────────────────────────────────────────────────────────
        (37.4464, 138.8512, "Nagaoka",      19.90),
        (37.1483, 138.2364, "Joetsu",       20.10),
        (38.0603, 138.4376, "Sado",         20.80),

        # ── Hokuriku ──────────────────────────────────────────────────────────
        (36.7500, 137.0167, "Takaoka",      19.60),
        (36.0652, 136.2216, "Sabae",        19.60),
        (36.4026, 136.4508, "Komatsu",      19.60),

        # ── Tokai ─────────────────────────────────────────────────────────────
        (35.4233, 136.7607, "Ogaki",        19.30),
        (34.7303, 136.5086, "Tsu",          19.50),
        (34.7180, 137.8515, "Iwata",        19.20),
        (34.7687, 137.9980, "Kakegawa",     19.40),
        (35.0956, 138.8635, "Numazu",       19.40),
        (35.1223, 138.9185, "Mishima",      19.40),

        # ── Kansai ────────────────────────────────────────────────────────────
        (34.6851, 135.8048, "Tenri",        19.50),
        (34.5733, 135.4828, "Sakai",        18.10),
        (34.8164, 135.5683, "Takatsuki",    18.50),
        (34.6930, 135.1940, "Akashi",       18.70),
        (34.2305, 135.1708, "Wakayama",     19.50),

        # ── Chugoku ───────────────────────────────────────────────────────────
        (35.4723, 133.0505, "Matsue",       20.20),
        (35.4281, 133.3309, "Yonago",       20.10),
        (35.5011, 134.2351, "Tottori",      20.20),
        (34.1785, 131.4737, "Yamaguchi",    20.20),
        (33.9578, 130.9414, "Shimonoseki",  19.40),

        # ── Shikoku ───────────────────────────────────────────────────────────
        (33.9196, 133.1810, "Niihama",      19.90),
        (33.8416, 132.7661, "Iyo",          20.10),
        (33.5624, 133.5373, "Nankoku",      20.20),
        (33.3636, 134.1520, "Muroto",       20.80),

        # ── Kyushu ────────────────────────────────────────────────────────────
        (32.7448, 129.8737, "Nagasaki",     19.50),
        (33.1799, 129.7150, "Sasebo",       19.80),
        (32.7503, 129.8780, "Nagasaki-C",   19.50),
        (31.9111, 131.4239, "Miyazaki",     19.60),
        (32.5833, 131.6667, "Nobeoka",      20.00),
        (31.7196, 131.0616, "Kobayashi",    20.40),
        (32.0686, 131.6514, "Hyuga",        20.00),
        (33.2635, 130.3009, "Karatsu",      19.80),
        (32.0134, 130.2110, "Izumi",        20.20),
        (31.3783, 130.8528, "Kanoya",       20.00),

        # ── Okinawa ───────────────────────────────────────────────────────────
        (26.3344, 127.8056, "Okinawa-C",    19.20),
        (26.2122, 127.6873, "Naha-Airport", 19.30),
        (24.3448, 124.1572, "Ishigaki",     20.80),
        (24.8056, 125.2811, "Miyakojima",   20.90),
        
        # ── 100 địa điểm bổ sung
        (43.7680, 142.3650, "Asahikawa",        20.40),
        (42.5220, 140.9700, "Noboribetsu",      20.20),
        (42.9240, 143.1970, "Obihiro",          20.30),
        (43.2000, 145.5800, "Nemuro",           20.70),
        (44.3300, 142.2300, "Nayoro",           20.50),
        (40.5900, 141.5000, "Misawa",           19.80),
        (40.6200, 140.4800, "Hirosaki",         20.00),
        (39.9500, 141.1300, "Kitakami",         20.10),
        (39.6800, 141.9000, "Kamaishi",         20.30),
        (38.2100, 140.8500, "Sendai-S",         19.50),
        (38.0000, 140.4500, "Yamagata",         19.80),
        (38.4500, 140.2500, "Shinjo",           20.30),
        (37.4000, 140.3800, "Koriyama",         19.60),
        (37.0500, 140.8800, "Iwaki-N",          19.90),
        (36.9500, 140.3500, "Shirakawa",        20.20),
        (36.5600, 139.8800, "Utsunomiya",       19.60),
        (36.4500, 139.8500, "Nikko",            20.40),
        (36.3500, 140.4500, "Mito",             19.50),
        (36.0000, 140.1000, "Tsuchiura",        19.30),
        (36.2000, 139.0000, "Takasaki",         19.40),
        (36.6500, 138.8500, "Numata",           20.50),
        (36.0500, 139.4000, "Kumagaya",         19.10),
        (35.9500, 139.7500, "Kasukabe",         18.80),
        (35.8500, 139.6500, "Urawa",            18.50),
        (35.7000, 139.9000, "Ichikawa",         18.00),
        (35.6000, 140.1200, "Chiba-C",          18.20),
        (35.5500, 140.1500, "Kisarazu",         19.00),
        (35.2500, 139.9000, "Tateyama",         19.80),
        (35.7800, 140.3500, "Narita-C",         19.20),
        (35.7500, 140.8000, "Choshi-C",         19.70),
        (35.6800, 139.7000, "Shinjuku-W",       17.10),
        (35.6500, 139.5000, "Chofu",            18.20),
        (35.7500, 139.4000, "Tokorozawa",       18.30),
        (35.5000, 139.4000, "Yamato",           18.70),
        (35.3500, 139.3500, "Hiratsuka",        19.00),
        (35.3000, 139.5500, "Kamakura-C",       19.20),
        (35.2500, 139.1500, "Odawara",          19.60),
        (35.2000, 139.0500, "Yugawara",         20.00),
        (35.1500, 138.6500, "Fuji",             19.50),
        (34.9800, 138.3800, "Shizuoka-C",       19.40),
        (34.7200, 137.7500, "Hamamatsu-C",      19.20),
        (35.6500, 138.5500, "Kofu-C",           19.90),
        (36.2500, 137.9500, "Matsumoto-C",      20.50),
        (36.6500, 138.1800, "Nagano-C",         20.10),
        (36.7500, 137.2000, "Toyama-C",         19.60),
        (36.5500, 136.6500, "Kanazawa-C",       19.50),
        (36.0500, 136.2000, "Fukui-C",          19.70),
        (35.1500, 136.9000, "Nagoya-C",         17.90),
        (35.4000, 136.7500, "Gifu-C",           19.40),
        (34.7500, 137.4000, "Toyohashi-C",      19.50),
        (34.6900, 135.5000, "Osaka-C",          17.70),
        (34.5800, 135.4800, "Sakai-C",          18.20),
        (34.8200, 135.5700, "Takatsuki-C",      18.60),
        (34.6800, 135.8000, "Nara-C",           19.30),
        (35.0000, 135.7500, "Kyoto-C",          18.80),
        (34.6900, 135.1800, "Kobe-C",           18.60),
        (34.6500, 133.9200, "Okayama-C",        19.30),
        (34.4800, 133.3800, "Fukuyama-C",       19.80),
        (34.3800, 132.4500, "Hiroshima-C",      19.30),
        (34.1800, 131.4700, "Yamaguchi-C",      20.30),
        (33.9500, 130.9500, "Shimonoseki-C",    19.50),
        (35.4700, 133.0500, "Matsue-C",         20.30),
        (35.5000, 134.2300, "Tottori-C",        20.30),
        (34.3400, 134.0500, "Takamatsu-C",      20.40),
        (34.0600, 134.5500, "Tokushima-C",      20.40),
        (33.8400, 132.7500, "Matsuyama-C",      20.20),
        (33.5600, 133.5300, "Kochi-C",          20.40),
        (33.5900, 130.4000, "Fukuoka-C",        18.60),
        (33.8800, 130.8700, "Kitakyushu-C",     18.90),
        (33.2500, 130.3000, "Saga-C",           19.90),
        (32.7500, 129.8800, "Nagasaki-C",       19.60),
        (32.8000, 130.7300, "Kumamoto-C",       19.60),
        (33.2400, 131.6000, "Oita-C",           19.50),
        (31.9000, 131.4200, "Miyazaki-C",       19.70),
        (31.6000, 130.5500, "Kagoshima-C",      19.60),
        (26.2100, 127.6800, "Naha-C",           19.60),
        (24.3500, 124.1500, "Ishigaki-C",       20.90),
        (43.8500, 144.1500, "Kitami-C",         20.50),
        (43.3000, 142.8000, "Furano",           20.60),
        (42.8000, 141.7000, "Chitose",          19.80),
        (40.8200, 140.7500, "Aomori-C",         20.40),
        (39.7000, 140.1000, "Akita-C",          20.20),
        (38.7500, 140.7000, "Naruko",           20.50),
        (38.2500, 141.0000, "Shiogama",         19.50),
        (37.7500, 140.4500, "Fukushima-C",      20.20),
        (36.8000, 139.9900, "Nasushiobara-C",   20.20),
        (36.3500, 139.0600, "Maebashi-C",       19.60),
        (36.3000, 139.1900, "Kiryu-C",          19.70),
        (36.0000, 139.5000, "Kuki",             19.00),
        (35.9000, 139.4000, "Kawagoe-C",        18.80),
        (35.7500, 140.1000, "Matsudo-C",        18.30),
        (35.7000, 139.7800, "Ueno-C",           17.50),
        (35.6500, 139.7000, "Shibuya-C",        17.30),
        (35.3500, 139.5500, "Fujisawa",         18.90),
        (35.2500, 139.1500, "Hakone-C",         20.40),
        (36.6500, 138.1800, "Suzaka-C",         20.30),
        (36.3000, 138.6000, "Saku-C",           20.70),
        (36.8500, 138.2500, "Myoko",            20.60),
        (36.7500, 137.0000, "Takaoka-C",        19.70),
        (34.6900, 135.1900, "Akashi-C",         18.80),
    ]

    sqm_est = 22.30  # start pristine, find most polluted influence
    for _clat, _clon, _cname, _csqm in _CITIES:
        _d = _km(lat, lon, _clat, _clon)
        _sqm_here = _csqm + _get_delta(_d)
        sqm_est = min(sqm_est, _sqm_here)

    sqm_est = max(17.5, min(22.3, round(sqm_est, 2)))

    # Convert SQM → Bortle class
    # Thresholds theo Wikipedia / Bortle 2001 / Sky & Telescope:
    #   Class 1:  21.76–22.0   Class 2: 21.6–21.75  Class 3: 21.3–21.6
    #   Class 4:  20.8–21.3    Class 4.5: 20.3–20.8 Class 5: 19.25–20.3
    #   Class 6:  18.5–19.25   Class 7: 18.0–18.5
    #   Class 8+: < 18.0
    if   sqm_est >= 21.76: bc = 1
    elif sqm_est >= 21.60: bc = 2
    elif sqm_est >= 21.30: bc = 3
    elif sqm_est >= 20.30: bc = 4   # gộp 4 và 4.5
    elif sqm_est >= 19.41: bc = 5
    elif sqm_est >= 18.50: bc = 6
    elif sqm_est >= 18.00: bc = 7
    elif sqm_est >= 17.62: bc = 8
    else:                  bc = 9

    return bc, sqm_est

# ── WEATHER FETCH ─────────────────────────────────────────────────────────────
# Các endpoint fallback theo thứ tự ưu tiên:
#   1. Primary: tất cả 3 models (JMA + ECMWF + GFS) — đầy đủ nhất
#   2. Fallback A: chỉ GFS + ECMWF (bỏ JMA) — nhẹ hơn, ít lỗi hơn
#   3. Fallback B: chỉ GFS — luôn hoạt động, không phụ thuộc Japan server
_FIELDS = "cloud_cover,cloud_cover_low,cloud_cover_mid,cloud_cover_high,relative_humidity_2m,wind_speed_10m,temperature_2m,precipitation"
_ENDPOINTS = [
    # (label, url_suffix)
    ("full",    f"&hourly={_FIELDS}&models=jma_msm,gfs_seamless,ecmwf_ifs025&wind_speed_unit=ms&timezone=auto"),
    ("no_jma",  f"&hourly={_FIELDS}&models=gfs_seamless,ecmwf_ifs025&wind_speed_unit=ms&timezone=auto"),
    ("gfs_only",f"&hourly={_FIELDS}&models=gfs_seamless&wind_speed_unit=ms&timezone=auto"),
]

@st.cache_data(ttl=1800, show_spinner=False)
def _fetch_weather_raw(lat, lon):
    """Raw API fetch với retry + multi-endpoint fallback.
    Returns (hourly_dict, utc_offset_seconds, endpoint_used_label, last_error)"""
    import time as _time
    base = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}"
    headers = {"User-Agent": "Mozilla/5.0 (AstroMapPro/7.0)"}
    last_error = None
    for ep_label, ep_suffix in _ENDPOINTS:
        url = base + ep_suffix
        for attempt in range(3):   # 3 lần thử mỗi endpoint (network có thể chập chờn)
            try:
                # Multi-model request (full/no_jma) nặng hơn, cần timeout dài hơn
                _timeout = 12 if ep_label != "gfs_only" else 8
                res = requests.get(url, headers=headers, timeout=_timeout)
                if res.status_code == 200:
                    j = res.json()
                    return j.get("hourly", {}), j.get("utc_offset_seconds", 32400), ep_label, None
                # 5xx = server lỗi → thử endpoint tiếp theo ngay
                last_error = f"HTTP {res.status_code}"
                if res.status_code >= 500:
                    break
            except requests.exceptions.Timeout:
                last_error = "timeout"
                # timeout → thử lại
            except requests.exceptions.ConnectionError as e:
                last_error = f"connection_error: {e.__class__.__name__}"
                _time.sleep(0.5 * (attempt + 1))  # backoff rồi thử lại — có thể chỉ là lỗi mạng tạm thời
                continue
            except Exception as e:
                last_error = f"{e.__class__.__name__}: {e}"
                break  # lỗi khác → chuyển endpoint ngay
    return {}, 32400, "offline", last_error

def fetch_weather_7days(lat, lon, source="JMA"):
    """Wrapper giữ nguyên interface cũ — delegate sang cached raw fetch."""
    hourly, utc_offset, ep_label, last_error = _fetch_weather_raw(lat, lon)
    return hourly, source, utc_offset, ep_label, last_error

def get_val(hourly, field, idx, prefer_jma=True):
    """
    Extract a single numeric value for a field at index idx.
    If prefer_jma: try _jma_msm first, fallback to _gfs_seamless.
    Else: try _gfs_seamless first, fallback to _jma_msm.
    Also tries bare key as last resort.
    Returns (float_value, source_used: 'JMA'|'GFS'|None)
    """
    order = ["_jma_msm", "_gfs_seamless"] if prefer_jma else ["_gfs_seamless", "_jma_msm"]
    labels = ["JMA", "GFS"] if prefer_jma else ["GFS", "JMA"]
    for suffix, label in zip(order, labels):
        lst = hourly.get(f"{field}{suffix}", [])
        if idx < len(lst) and lst[idx] is not None:
            return float(lst[idx]), label
    # bare key fallback
    lst = hourly.get(field, [])
    if idx < len(lst) and lst[idx] is not None:
        return float(lst[idx]), "?"
    return 0.0, None

def _get_raw(hourly, field, suffix, idx):
    """Get raw value for a specific model suffix. Returns None if missing."""
    lst = hourly.get(f"{field}{suffix}", [])
    if idx < len(lst) and lst[idx] is not None:
        return float(lst[idx])
    return None

def get_val_blended(hourly, field, idx, day_offset):
    """
    Weighted blend of JMA + ECMWF + GFS based on day_offset.
    Day 0-3: JMA x0.60 + ECMWF x0.30 + GFS x0.10  (JMA MSM 3km grid, best short-range for Japan)
    Day 4-7: ECMWF x0.55 + GFS x0.30 + JMA x0.15  (JMA MSM coverage ends ~day 3.5)
    Re-normalises weights if any model has missing data.
    Returns (float_value, label_string)
    """
    jma   = _get_raw(hourly, field, "_jma_msm",      idx)
    ecmwf = _get_raw(hourly, field, "_ecmwf_ifs025",  idx)
    gfs   = _get_raw(hourly, field, "_gfs_seamless",  idx)

    if day_offset <= 3:
        weights = {"jma": 0.40, "ecmwf": 0.50, "gfs": 0.10}
    else:
        weights = {"jma": 0.14, "ecmwf": 0.56, "gfs": 0.30}

    vals  = {"jma": jma, "ecmwf": ecmwf, "gfs": gfs}
    avail = {k: v for k, v in vals.items() if v is not None}
    if not avail:
        return 0.0, None

    total_w = sum(weights[k] for k in avail)
    blended = sum(weights[k] * v for k, v in avail.items()) / total_w
    return round(blended, 1), "Blend"

# ── COMPUTED STATE ────────────────────────────────────────────────────────────
bortle_class, sqm_val = calculate_accurate_bortle(st.session_state.lat, st.session_state.lon)
ra_val, dec_val = calculate_zenith_ra_dec(st.session_state.lat, st.session_state.lon)

JST = timezone(timedelta(hours=9))

# ── Night-start offset ─────────────────────────────────────────────────────────
# A "night" runs 18:00 → 06:00 next day.
# If current JST time is 00:00–17:59 we are still inside last-night's second half
# (00:00–06:00 already passed, 18:00 tonight is the NEXT upcoming block).
# So: if hour < 18, "night 0" = today's evening (18:00 today → 06:00 tomorrow),
#     which means we base target_date on today's date.
# The past-data problem (18:00-23:59 gone after midnight): we fix it by
# skipping slots that are in the past when rendering the table.
_now_jst        = datetime.now(JST)
# If 00:00~05:59 → we're still in the previous night (18:00 yesterday → 06:00 today)
# so shift base back 1 day to keep tonight's 00:00~06:00 slots visible
if _now_jst.hour < 6:
    _night_base_jst = _now_jst - timedelta(days=1)
else:
    _night_base_jst = _now_jst
# date_options i=0 → tonight (18:00 of _night_base_jst)
_jp_wd = ["月", "火", "水", "木", "金", "土", "日"]
def _jp_date(d, suffix):
    return f"{d.month}月{d.day}日{suffix}({_jp_wd[d.weekday()]})"
date_options = [
    f"{_jp_date(_night_base_jst+timedelta(days=i), '夜')} → {_jp_date(_night_base_jst+timedelta(days=i+1), '朝')}"
    for i in range(7)
]

target_date = (_night_base_jst + timedelta(days=st.session_state.day_offset)).replace(tzinfo=None)
next_date   = target_date + timedelta(days=1)

moon_pct, moon_text = get_moon_phase_percent(target_date)

prefer_jma = (st.session_state.weather_source not in ["US (GFS)", "EU (ECMWF)"])
use_blend  = (st.session_state.weather_source == "🔀 Blend (JMA+ECMWF+GFS)")
use_ecmwf  = (st.session_state.weather_source == "EU (ECMWF)")
hourly_data, _, _loc_utc_offset, _ep_label, _last_error = fetch_weather_7days(
    st.session_state.lat, st.session_state.lon, st.session_state.weather_source
)

# ── AUTO-DETECT JMA COVERAGE cho ngày được chọn ───────────────────────────────
# JMA MSM chỉ có ~3-4 ngày. Nếu user chọn JMA nhưng ngày đó JMA toàn null
# → tự động dùng GFS thay thế (prefer_jma=False) mà không cần user đổi tay.
def _jma_has_data_for_date(hourly, date_prefix):
    """Trả về True nếu JMA có ít nhất 1 giá trị không-None cho ngày date_prefix."""
    times = hourly.get("time", [])
    cc_jma = hourly.get("cloud_cover_jma_msm", [])
    for i, t in enumerate(times):
        if t.startswith(date_prefix) and i < len(cc_jma) and cc_jma[i] is not None:
            return True
    return False

# Auto-switch: chỉ can thiệp khi đang dùng JMA đơn lẻ, không đụng Blend
if st.session_state._source_auto and hourly_data:
    _cur = st.session_state.weather_source
    if _cur not in ("🔀 Blend (JMA+ECMWF+GFS)", "US (GFS)", "EU (ECMWF)"):
        jma_ok = (_jma_has_data_for_date(hourly_data, target_date.strftime("%Y-%m-%d")) or
                  _jma_has_data_for_date(hourly_data, next_date.strftime("%Y-%m-%d")))
        if not jma_ok:
            st.session_state.weather_source = "US (GFS)"

# Sau auto-switch, cập nhật lại flags theo source hiện tại
prefer_jma = (st.session_state.weather_source not in ["US (GFS)", "EU (ECMWF)"])
use_blend  = (st.session_state.weather_source == "🔀 Blend (JMA+ECMWF+GFS)")
use_ecmwf  = (st.session_state.weather_source == "EU (ECMWF)")

# UTC offset của location hiện tại (tính bằng giây) — dùng cho moon altitude
loc_utc_offset_h = _loc_utc_offset / 3600.0  # đổi sang giờ, ví dụ JST=+9, CST=-6

desired_slots = [
    (target_date.year, target_date.month, target_date.day, 18, "18:00", target_date.strftime("%Y-%m-%d")),
    (target_date.year, target_date.month, target_date.day, 19, "19:00", target_date.strftime("%Y-%m-%d")),
    (target_date.year, target_date.month, target_date.day, 20, "20:00", target_date.strftime("%Y-%m-%d")),
    (target_date.year, target_date.month, target_date.day, 21, "21:00", target_date.strftime("%Y-%m-%d")),
    (target_date.year, target_date.month, target_date.day, 22, "22:00", target_date.strftime("%Y-%m-%d")),
    (target_date.year, target_date.month, target_date.day, 23, "23:00", target_date.strftime("%Y-%m-%d")),
    (next_date.year, next_date.month, next_date.day, 0,  "00:00", next_date.strftime("%Y-%m-%d")),
    (next_date.year, next_date.month, next_date.day, 1,  "01:00",    next_date.strftime("%Y-%m-%d")),
    (next_date.year, next_date.month, next_date.day, 2,  "02:00",    next_date.strftime("%Y-%m-%d")),
    (next_date.year, next_date.month, next_date.day, 3,  "03:00",    next_date.strftime("%Y-%m-%d")),
    (next_date.year, next_date.month, next_date.day, 4,  "04:00",    next_date.strftime("%Y-%m-%d")),
    (next_date.year, next_date.month, next_date.day, 5,  "05:00",    next_date.strftime("%Y-%m-%d")),
    (next_date.year, next_date.month, next_date.day, 6,  "06:00",    next_date.strftime("%Y-%m-%d")),
]

# Filter out slots that are already in the past (only for tonight, day_offset=0)
_now_naive = _now_jst.replace(tzinfo=None)
def _slot_is_future(yr, mo, dy, hr):
    # Include the current hour slot (e.g. 20:01 → still show 20:00 row)
    slot_dt = datetime(yr, mo, dy, hr, 0) + timedelta(hours=1)
    return slot_dt > _now_naive

_full_night_slots = list(desired_slots)
if st.session_state.day_offset == 0:
    desired_slots = [(yr,mo,dy,hr,lbl,dpfx) for yr,mo,dy,hr,lbl,dpfx in desired_slots
                     if _slot_is_future(yr,mo,dy,hr)]

@st.cache_data(ttl=1800, show_spinner=False)
def _build_night_data(lat, lon, slots, hourly_data_frozen, weather_source, loc_utc_offset_h):
    """Cache toàn bộ vòng lặp tính weather table + moon/sun/MW altitudes.
    Key cache = (lat, lon, slots, source) — chỉ recompute khi thực sự đổi ngày/địa điểm/source."""
    # hourly_data_frozen là tuple-of-items để hashable
    hourly = dict(hourly_data_frozen) if hourly_data_frozen else {}

    _prefer_jma = weather_source not in ["US (GFS)", "EU (ECMWF)"]
    _use_blend  = weather_source == "🔀 Blend (JMA+ECMWF+GFS)"
    _use_ecmwf  = weather_source == "EU (ECMWF)"

    # day_offset chỉ ảnh hưởng blend weight — dùng slot index 0 làm proxy
    _day_offset_proxy = 0
    if slots:
        yr0, mo0, dy0 = slots[0][0], slots[0][1], slots[0][2]
        from datetime import date as _date
        _today = _date.today()
        _day_offset_proxy = (_date(yr0, mo0, dy0) - _today).days
        _day_offset_proxy = max(0, min(6, _day_offset_proxy))

    out_table  = []
    out_hours  = []
    out_moon   = []
    out_sun    = []
    out_mw     = []
    out_debug  = {"low": 0, "mid": 0, "high": 0, "total": 0}
    out_srcs   = set()

    times_list = hourly.get("time", [])

    for yr, mo, dy, hr_local, label, date_prefix in slots:
        out_hours.append(label)
        out_moon.append(calculate_exact_moon_altitude_ephem(lat, lon, yr, mo, dy, hr_local, loc_utc_offset_h))
        out_sun.append(calculate_exact_sun_altitude_ephem(lat, lon, yr, mo, dy, hr_local, loc_utc_offset_h))
        mw_alt, _ = calculate_milkyway_altitude(lat, lon, yr, mo, dy, hr_local, loc_utc_offset_h)
        out_mw.append(mw_alt)

        if not times_list:
            continue

        target_ts = f"{date_prefix}T{hr_local:02d}:00"
        idx = next((i for i, t in enumerate(times_list) if t.startswith(target_ts)), -1)
        if idx == -1:
            continue

        if _use_blend:
            avg_cloud, src1 = get_val_blended(hourly, "cloud_cover",          idx, _day_offset_proxy)
            low_c,     _    = get_val_blended(hourly, "cloud_cover_low",       idx, _day_offset_proxy)
            mid_c,     _    = get_val_blended(hourly, "cloud_cover_mid",       idx, _day_offset_proxy)
            high_c,    _    = get_val_blended(hourly, "cloud_cover_high",      idx, _day_offset_proxy)
            humid,     _    = get_val_blended(hourly, "relative_humidity_2m",  idx, _day_offset_proxy)
            wind_speed,_    = get_val_blended(hourly, "wind_speed_10m",        idx, _day_offset_proxy)
            temp_val,  _    = get_val_blended(hourly, "temperature_2m",        idx, _day_offset_proxy)
            precip_val,_    = get_val_blended(hourly, "precipitation",         idx, _day_offset_proxy)
            if src1: out_srcs.add(src1)
        elif _use_ecmwf:
            avg_cloud  = _get_raw(hourly, "cloud_cover",          "_ecmwf_ifs025", idx) or 0.0
            low_c      = _get_raw(hourly, "cloud_cover_low",       "_ecmwf_ifs025", idx) or 0.0
            mid_c      = _get_raw(hourly, "cloud_cover_mid",       "_ecmwf_ifs025", idx) or 0.0
            high_c     = _get_raw(hourly, "cloud_cover_high",      "_ecmwf_ifs025", idx) or 0.0
            humid      = _get_raw(hourly, "relative_humidity_2m",  "_ecmwf_ifs025", idx) or 0.0
            wind_speed = _get_raw(hourly, "wind_speed_10m",        "_ecmwf_ifs025", idx) or 0.0
            temp_val   = _get_raw(hourly, "temperature_2m",        "_ecmwf_ifs025", idx) or 0.0
            precip_val = _get_raw(hourly, "precipitation",         "_ecmwf_ifs025", idx) or 0.0
            src1 = "ECMWF"
            out_srcs.add("ECMWF")
        else:
            avg_cloud, src1 = get_val(hourly, "cloud_cover",          idx, _prefer_jma)
            low_c,     _    = get_val(hourly, "cloud_cover_low",      idx, _prefer_jma)
            mid_c,     _    = get_val(hourly, "cloud_cover_mid",      idx, _prefer_jma)
            high_c,    _    = get_val(hourly, "cloud_cover_high",     idx, _prefer_jma)
            humid,     _    = get_val(hourly, "relative_humidity_2m", idx, _prefer_jma)
            wind_speed,_    = get_val(hourly, "wind_speed_10m",       idx, _prefer_jma)
            temp_val,  _    = get_val(hourly, "temperature_2m",       idx, _prefer_jma)
            precip_val,_    = get_val(hourly, "precipitation",        idx, _prefer_jma)
            if src1: out_srcs.add(src1)

        if len(out_table) == 0:
            out_debug = {"low": int(low_c), "mid": int(mid_c), "high": int(high_c), "total": int(avg_cloud)}

        score = 100 - avg_cloud
        if score >= 92:   stars = "⭐⭐⭐⭐"
        elif score >= 75: stars = "⭐⭐⭐☆"
        elif score >= 50: stars = "⭐⭐☆☆"
        elif score >= 20: stars = "⭐☆☆☆"
        else:             stars = "☆☆☆☆"

        out_table.append({
            "⏰": label,
            "☁️": f"{int(avg_cloud)}%",
            "💧": f"{int(humid)}%",
            "💨": f"{round(wind_speed,1)}m/s",
            "📸": stars,
            "_temp": temp_val,
            "_precip": precip_val,
        })

    return out_table, out_hours, out_moon, out_sun, out_mw, out_debug, out_srcs

# Chuyển hourly_data sang dạng hashable để cache key hoạt động
_hourly_frozen = tuple(
    (k, tuple(v) if isinstance(v, list) else v)
    for k, v in (hourly_data.items() if hourly_data else [])
)

# ── PREFETCH TẤT CẢ 7 ĐÊM ngay sau khi có hourly_data ────────────────────────
# Mục đích: warm up cache cho toàn bộ 7 ngày ngay khi chọn location.
# Khi user bấm Next/Prev → _build_night_data đã có cache → gần như instant.
# Chạy tuần tự (không thread) vì @st.cache_data không thread-safe khi write.
def _make_slots_for_offset(base_jst, day_off):
    td = (base_jst + timedelta(days=day_off)).replace(tzinfo=None)
    nd = td + timedelta(days=1)
    return tuple([
        (td.year, td.month, td.day, 18, "18:00", td.strftime("%Y-%m-%d")),
        (td.year, td.month, td.day, 19, "19:00", td.strftime("%Y-%m-%d")),
        (td.year, td.month, td.day, 20, "20:00", td.strftime("%Y-%m-%d")),
        (td.year, td.month, td.day, 21, "21:00", td.strftime("%Y-%m-%d")),
        (td.year, td.month, td.day, 22, "22:00", td.strftime("%Y-%m-%d")),
        (td.year, td.month, td.day, 23, "23:00", td.strftime("%Y-%m-%d")),
        (nd.year, nd.month, nd.day,  0, "00:00", nd.strftime("%Y-%m-%d")),
        (nd.year, nd.month, nd.day,  1, "01:00", nd.strftime("%Y-%m-%d")),
        (nd.year, nd.month, nd.day,  2, "02:00", nd.strftime("%Y-%m-%d")),
        (nd.year, nd.month, nd.day,  3, "03:00", nd.strftime("%Y-%m-%d")),
        (nd.year, nd.month, nd.day,  4, "04:00", nd.strftime("%Y-%m-%d")),
        (nd.year, nd.month, nd.day,  5, "05:00", nd.strftime("%Y-%m-%d")),
        (nd.year, nd.month, nd.day,  6, "06:00", nd.strftime("%Y-%m-%d")),
    ])

# Prefetch các ngày KHÁC: skip hoàn toàn ngay sau khi đổi location,
# lần rerun tiếp theo mới prefetch theo thứ tự ngày liền kề trước.
if st.session_state._skip_prefetch:
    st.session_state._skip_prefetch = False
else:
    _day_off = st.session_state.day_offset
    _prio = []
    if _day_off + 1 < 7: _prio.append(_day_off + 1)
    if _day_off - 1 >= 0: _prio.append(_day_off - 1)
    for _p in range(7):
        if _p not in _prio and _p != _day_off:
            _prio.append(_p)
    for _poff in _prio:
        try:
            _build_night_data(
                st.session_state.lat, st.session_state.lon,
                _make_slots_for_offset(_night_base_jst, _poff),
                _hourly_frozen,
                st.session_state.weather_source,
                loc_utc_offset_h,
            )
        except Exception:
            pass

(weather_table_data, hours_labels, moon_altitudes, sun_altitudes,
 milkyway_altitudes, current_cloud_debug, sources_used) = _build_night_data(
    st.session_state.lat, st.session_state.lon,
    tuple(desired_slots),
    _hourly_frozen,
    st.session_state.weather_source,
    loc_utc_offset_h,
)
sources_used = set(sources_used)  # trả về từ cache là frozenset hoặc set, đảm bảo là set

# Label thực tế đã dùng — phân biệt auto-fallback với user chọn tay
if use_blend:
    active_source_label = "🔀 Blend (JMA+ECMWF+GFS)"
elif "ECMWF" in sources_used:
    active_source_label = "EU (ECMWF IFS025)"
elif "JMA" in sources_used and "GFS" in sources_used:
    active_source_label = "JMA + US (GFS)"
elif "GFS" in sources_used and prefer_jma:
    # User chọn JMA nhưng JMA không có data → auto-fallback
    active_source_label = "US (GFS) [auto-fallback]"
elif "GFS" in sources_used:
    active_source_label = "US (GFS)"
elif "JMA" in sources_used:
    active_source_label = "JMA"
else:
    active_source_label = st.session_state.weather_source

# ── NIGHT VERDICT (full night 18:00~06:00) ───────────────────────────────────
def _build_night_verdict(table_data, sun_alts=None, moon_illum=None):
    """Tính đánh giá tổng hợp cho cả đêm 18:00~06:00, dựa chủ yếu trên Cloud %
    (và precip/temp để phân biệt mưa/tuyết) — giống Clear Outside / Astrospheric
    nhưng đơn giản, dễ hiểu: PERFECT NIGHT / GOOD STARRY NIGHT / FAIR SKIES /
    PATCHY CLEAR / PARTLY CLOUDY / CLOUDY NIGHT / RAINY NIGHT / SNOWY NIGHT / TOO BRIGHT.

    'Giờ tốt' = slot trời đã tối thiên văn (sun_alt ≤ -12°) và cloud ≤ 25%.

    Trả về dict với tier, icon, stars, sub, màu sắc, v.v."""
    if not table_data:
        return None
    # 13 slots = 18:00..23:00 + 00:00..06:00, nhưng "đêm" chỉ tính 12 giờ (18:00→06:00).
    # Slot 06:00 cuối chỉ là điểm mốc kết thúc (đã là sáng), không tính vào giờ clear.
    if len(table_data) > 12:
        table_data = table_data[:-1]
        if sun_alts is not None:
            sun_alts = sun_alts[:-1]
    if sun_alts is None:
        sun_alts = [-90] * len(table_data)

    total = 0
    rain_hours = 0
    snow_hours = 0
    cloud_vals = []
    # streak[i] = True nếu slot i là "giờ tốt" (trong khung tối thiên văn)
    good_flags = []
    for r, sa in zip(table_data, sun_alts):
        # Chỉ tính các slot trời đã tối thiên văn thực sự (sun_alt ≤ -12°)
        if sa is not None and sa > -12:
            continue
        total += 1
        cloud_str = r.get("☁️", "100%")
        precip    = r.get("_precip", 0.0) or 0.0
        temp_val  = r.get("_temp")
        cloud_pct = int(cloud_str.replace("%","")) if cloud_str.replace("%","").isdigit() else 100
        cloud_vals.append(cloud_pct)

        if precip >= 0.3:
            if temp_val is not None and temp_val < 2.0:
                snow_hours += 1
            else:
                rain_hours += 1

        is_good = (precip < 0.3) and (cloud_pct <= 25)
        good_flags.append(is_good)

    # ── Không có khung giờ tối thiên văn (đêm hè, trời sáng suốt) ──────────────
    if total == 0:
        return {"tier": "TOO BRIGHT", "icon": "🌃", "stars": "✕",
                "sub": "no astro-dark",
                "color": "#94a3b8", "border": "rgba(148,163,184,0.55)",
                "bg": "rgba(10,14,22,0.88)", "anim": "blink-warn",
                "good_hours": 0, "total": 0}

    # ── Tìm cửa sổ liên tiếp dài nhất có điều kiện tốt (longest good streak) ──
    best_streak = 0
    cur_streak = 0
    for g in good_flags:
        if g:
            cur_streak += 1
            best_streak = max(best_streak, cur_streak)
        else:
            cur_streak = 0
    good_hours = sum(good_flags)  # tổng giờ tốt (rời rạc), dùng cho sub-label
    avg_cloud = round(sum(cloud_vals) / len(cloud_vals)) if cloud_vals else 100

    # ── Trăng sáng? (ảnh hưởng đến chụp Milky Way / DSO mờ) ────────────────────
    bright_moon = (moon_illum is not None) and (moon_illum >= 50)

    # ── Smart Labeling: ưu tiên Cloud % trung bình của cả đêm, dễ hiểu ─────────
    if snow_hours >= int(total * 0.3):
        tier = "SNOWY NIGHT"
        icon = "❄️"; stars = "✕"
        color = "#bae6fd"; border = "rgba(186,230,253,0.70)"
        bg    = "rgba(8,18,30,0.88)"; anim = "blink-warn"
        sub   = f"{snow_hours}h snow"
    elif rain_hours >= int(total * 0.3):
        tier = "RAINY NIGHT"
        icon = "🌧️"; stars = "✕"
        color = "#fca5a5"; border = "rgba(239,68,68,0.70)"
        bg    = "rgba(30,8,8,0.88)"; anim = "blink-warn"
        sub   = f"{rain_hours}h rain"
    elif best_streak >= 3 and not bright_moon:
        tier = "PERFECT NIGHT"
        icon = "🌌"; stars = "★★★★"
        color = "#6ee7b7"; border = "rgba(52,211,153,0.75)"
        bg    = "rgba(5,25,18,0.88)"; anim = "blink-smile"
        sub   = f"avg cloud {avg_cloud}%, {best_streak}h clear"
    elif best_streak >= 3 and bright_moon:
        tier = "GOOD STARRY NIGHT"
        icon = "🔭"; stars = "★★★"
        color = "#93c5fd"; border = "rgba(96,165,250,0.70)"
        bg    = "rgba(6,16,30,0.88)"; anim = "blink-smile"
        sub   = f"avg cloud {avg_cloud}%, bright moon"
    elif best_streak >= 1:
        tier = "FAIR SKIES"
        icon = "🌤️"; stars = "★★"
        color = "#fde68a"; border = "rgba(251,191,36,0.65)"
        bg    = "rgba(20,16,4,0.88)"; anim = "blink-neutral"
        sub   = f"avg cloud {avg_cloud}%, {best_streak}h window"
    elif avg_cloud <= 40:
        tier = "PATCHY CLEAR"
        icon = "🌥️"; stars = "★"
        color = "#fef08a"; border = "rgba(250,204,21,0.55)"
        bg    = "rgba(20,16,4,0.88)"; anim = "blink-neutral"
        sub   = f"avg cloud {avg_cloud}%, no long window"
    elif avg_cloud <= 70:
        tier = "PARTLY CLOUDY"
        icon = "🌥️"; stars = "★"
        color = "#fdba74"; border = "rgba(251,146,60,0.55)"
        bg    = "rgba(20,12,4,0.88)"; anim = "blink-neutral"
        sub   = f"avg cloud {avg_cloud}%"
    else:
        tier = "CLOUDY NIGHT"
        icon = "☁️"; stars = "✕"
        color = "#94a3b8"; border = "rgba(148,163,184,0.55)"
        bg    = "rgba(10,14,22,0.88)"; anim = "blink-warn"
        sub   = f"avg cloud {avg_cloud}%"

    return {"tier": tier, "icon": icon, "stars": stars, "sub": sub,
            "color": color, "border": border, "bg": bg, "anim": anim,
            "good_hours": good_hours, "best_streak": best_streak, "total": total}

# ── GREAT NIGHT SCAN — quét 27 địa điểm yêu thích × 7 ngày tới ───────────────
# Điều kiện thông báo (AND):
#   1) Moon illumination < 32%
#   2) Có ít nhất 1/27 địa điểm đầu (sao xanh) đạt tier == "PERFECT NIGHT"
#   3) Chỉ báo NGÀY SỚM NHẤT thoả mãn (1-7 ngày tới)
_FAVORITE_LOCATIONS = [(n, c) for n, c in LOCATION_DATABASE.items()
                       if (lambda nm: nm.split(".")[0].strip().isdigit() and int(nm.split(".")[0].strip()) <= 27)(n)]

def _haversine_km(lat1, lon1, lat2, lon2):
    """Khoảng cách Haversine giữa 2 điểm (km)."""
    R = 6371.0
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon/2)**2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

def _run_great_night_scan():
    """Quét 7 ngày tới cho 27 địa điểm yêu thích, trả về dict kết quả ngày sớm nhất
    có PERFECT NIGHT + moon < 32%.
    - all_locs: danh sách TẤT CẢ địa điểm PERFECT NIGHT trong ngày đó (sau khi lọc <20km)
    - loc_name / loc_coords: địa điểm đầu tiên (để hiển thị banner chính)
    Trả về None nếu không có ngày nào thoả."""
    for day_off in range(7):
        d = (_night_base_jst + timedelta(days=day_off)).replace(tzinfo=None)
        moon_illum, _ = get_moon_phase_percent(d)
        if moon_illum >= 32:
            continue
        slots = _make_slots_for_offset(_night_base_jst, day_off)
        perfect_locs = []  # (loc_name, loc_coords, verdict) tất cả địa điểm pass
        for loc_name, loc_coords in _FAVORITE_LOCATIONS:
            lat, lon = loc_coords
            try:
                hourly, _, utc_off, _, _ = fetch_weather_7days(lat, lon, st.session_state.weather_source)
            except Exception:
                continue
            if not hourly:
                continue
            frozen = tuple(
                (k, tuple(v) if isinstance(v, list) else v)
                for k, v in hourly.items()
            )
            try:
                table, _, _, sun_alts, *_r = _build_night_data(
                    lat, lon, slots, frozen, st.session_state.weather_source, utc_off / 3600.0
                )
            except Exception:
                continue
            verdict = _build_night_verdict(table, sun_alts, moon_illum)
            if verdict and verdict["tier"] == "PERFECT NIGHT":
                perfect_locs.append((loc_name, loc_coords, verdict))

        if not perfect_locs:
            continue

        # ── Lọc bỏ các địa điểm gần nhau < 20km (giữ lại địa điểm đầu tiên) ──
        deduped = []
        for entry in perfect_locs:
            _, coords, _ = entry
            too_close = False
            for kept in deduped:
                _, kept_coords, _ = kept
                if _haversine_km(coords[0], coords[1], kept_coords[0], kept_coords[1]) < 20:
                    too_close = True
                    break
            if not too_close:
                deduped.append(entry)

        first_name, first_coords, first_verdict = deduped[0]
        return {
            "date": d, "day_off": day_off,
            "loc_name": first_name, "loc_coords": first_coords,
            "moon_illum": moon_illum, "verdict": first_verdict,
            "all_locs": deduped,  # [(loc_name, loc_coords, verdict), ...]
        }
    return None

# ── MAP ───────────────────────────────────────────────────────────────────────
# Add top margin so the in-map tile buttons are not obscured by Streamlit toolbar
st.markdown("<div style='margin-top:38px'></div>", unsafe_allow_html=True)

# ── MAP tile switcher — ASCII keys only, no emoji in any string passed to folium ──
_TILE_SAT_URL  = 'https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}'
_TILE_STR_URL  = 'https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png'

if st.session_state.map_tile not in ("satellite", "street", "windy"):
    st.session_state.map_tile = "windy"

# ── Folium map — location/zoom từ session state (key cố định → không recreate) ──
# prefer_location=False: KHÔNG reset vị trí camera khi rerun — chỉ set lần đầu.
# Điều này là chìa khoá giúp pan/zoom mượt: Streamlit không can thiệp vào
# camera position sau mỗi rerun.
m = folium.Map(
    location=st.session_state.map_center,
    zoom_start=st.session_state.zoom,
    tiles=None,           # không load tile mặc định; tile được inject qua JS bên dưới
    prefer_canvas=True,   # dùng Canvas renderer → ít DOM node hơn, scroll mượt hơn
)

# ── Tile layers (chỉ để JS switchTile có thể gọi; không load ngay) ──
_street_layer = folium.TileLayer(
    tiles=_TILE_STR_URL, attr='CartoDB Voyager', name='street', overlay=False
)
_street_layer.add_to(m)

folium.TileLayer(
    tiles='https://{s}.tiles.openrailwaymap.org/standard/{z}/{x}/{y}.png',
    name='OpenRailwayMap', overlay=True, control=True, opacity=0.25, attr='OpenRailwayMap'
).add_to(m)

# ── Combined BottomRight control: [📍 Label  LPM] + [Windy|Satellite|Street] ──
# Gộp thành một control duy nhất (column) để kiểm soát khoảng cách chính xác.
from folium import MacroElement
from jinja2 import Template

_lpm_url = (f"https://lightpollutionmap.app/"
            f"?lat={st.session_state.lat:.4f}&lng={st.session_state.lon:.4f}&zoom=10")

_COMBINED_CTRL_TEMPLATE = Template("""
{% macro script(this, kwargs) %}
(function(){
  // ── localStorage keys ─────────────────────────────────────────────────────
  var LS_TILE   = 'astro_map_tile';
  var LS_W_LAT  = 'astro_windy_lat';
  var LS_W_LON  = 'astro_windy_lon';
  var LS_W_ZOOM = 'astro_windy_zoom';

  // ── Windy defaults (Kanto, zoom 7) ────────────────────────────────────────
  var _W_DEF_LAT  = 35.80;
  var _W_DEF_LON  = 139.50;
  var _W_DEF_ZOOM = 7;

  function _lsGet(k, def) {
    try { var v = localStorage.getItem(k); return (v !== null) ? v : def; } catch(e) { return def; }
  }
  function _lsSet(k, v) { try { localStorage.setItem(k, String(v)); } catch(e){} }

  function _buildWindySrc(lat, lon, zoom) {
    var latStr = parseFloat(lat).toFixed(4);
    var lonStr = parseFloat(lon).toFixed(4);
    return 'https://embed.windy.com/embed2.html'
      + '?lat=' + latStr
      + '&lon=' + lonStr
      + '&detailLat=' + latStr
      + '&detailLon=' + lonStr
      + '&width=650&height=450&zoom=' + Math.round(zoom)
      + '&level=surface&overlay=rain&product=ecmwf'
      + '&menu=&message=true&marker=' + latStr + ',' + lonStr + '&calendar=now'
      + '&pressure=&type=map&location=coordinates'
      + '&detail=&metricWind=default&metricTemp=default&radarRange=-1';
  }

  var _windyFrame = null;

  function _ensureWindyFrame(mapEl) {
    if (_windyFrame) return;
    _windyFrame = mapEl.querySelector('#astro-windy-iframe');
    if (_windyFrame) return;
    var lat  = parseFloat(_lsGet(LS_W_LAT,  _W_DEF_LAT));
    var lon  = parseFloat(_lsGet(LS_W_LON,  _W_DEF_LON));
    var zoom = parseInt(  _lsGet(LS_W_ZOOM, _W_DEF_ZOOM), 10);
    _windyFrame = document.createElement('iframe');
    _windyFrame.id  = 'astro-windy-iframe';
    _windyFrame.src = _buildWindySrc(lat, lon, zoom);
    _windyFrame.style.cssText = (
      'position:absolute;top:0;left:0;width:100%;height:100%;'
      + 'border:none;z-index:500;display:none;border-radius:inherit;'
    );
    _windyFrame.setAttribute('allowfullscreen', '');
    _windyFrame.setAttribute('sandbox',
      'allow-scripts allow-same-origin allow-forms allow-popups allow-top-navigation');
    mapEl.style.position = 'relative';
    mapEl.appendChild(_windyFrame);
  }

  window.flyWindy = function(lat, lon, zoom) {
    zoom = zoom || 9;
    _lsSet(LS_W_LAT,  lat);
    _lsSet(LS_W_LON,  lon);
    _lsSet(LS_W_ZOOM, zoom);
    if (_windyFrame) { _windyFrame.src = _buildWindySrc(lat, lon, zoom); }
  };

  var CombinedCtrl = L.Control.extend({
    options: { position: 'bottomright' },
    onAdd: function(map) {
      // ── Outer column wrapper ───────────────────────────────────────────────
      var col = L.DomUtil.create('div', '');
      col.style.cssText = (
        'display:flex;flex-direction:column;align-items:flex-end;'
        + 'gap:6px;margin-bottom:38px;'
      );
      L.DomEvent.disableClickPropagation(col);

      // ── Row 1: 📍 Label + LPM ─────────────────────────────────────────────
      var infoRow = L.DomUtil.create('div', '', col);
      infoRow.style.cssText = (
        'display:flex;align-items:center;gap:6px;'
        + 'background:rgba(15,23,42,0.88);border:1px solid #334155;'
        + 'border-radius:8px;padding:5px 8px;'
        + 'box-shadow:0 2px 8px rgba(0,0,0,0.6);'
      );

      var pin = L.DomUtil.create('span', '', infoRow);
      pin.innerHTML = '&#128205;';
      pin.style.cssText = 'font-size:13px;flex-shrink:0;line-height:1;';

      var loc = L.DomUtil.create('span', '', infoRow);
      loc.textContent = '{{ this.location_name }}';
      loc.style.cssText = 'color:#e2e8f0;font-size:12px;font-weight:600;'
        + 'white-space:nowrap;display:inline-block;';

      var a = L.DomUtil.create('a', '', infoRow);
      a.href = '{{ this.lpm_url }}';
      a.target = '_blank'; a.rel = 'noopener'; a.title = 'Light Pollution Map';
      a.textContent = 'LPM';
      a.style.cssText = 'display:inline-flex;align-items:center;justify-content:center;'
        + 'background:rgba(124,58,237,0.22);border:1.5px solid rgba(124,58,237,0.65);'
        + 'border-radius:6px;padding:2px 8px;text-decoration:none;'
        + 'color:#a78bfa;font-size:12px;font-weight:700;'
        + 'transition:background 0.2s;white-space:nowrap;cursor:pointer;flex-shrink:0;';
      a.onmouseover = function(){ a.style.background = 'rgba(124,58,237,0.42)'; };
      a.onmouseout  = function(){ a.style.background = 'rgba(124,58,237,0.22)'; };

      // ── SCAN button — hidden; triggered by typing "scan" in search box ─────
      // (kept as a JS function so search control can call it)
      window._triggerScan = function() {
        map.fire('click', { latlng: L.latLng(99.9, 99.9) });
      };

      // ── Row 2: Windy | Satellite | Street ─────────────────────────────────
      var tileRow = L.DomUtil.create('div', '', col);
      tileRow.style.cssText = (
        'display:flex;gap:4px;background:rgba(15,23,42,0.88);'
        + 'border:1px solid #334155;border-radius:8px;padding:5px 8px;'
        + 'box-shadow:0 2px 8px rgba(0,0,0,0.6);'
      );

      var tiles = {
        satellite: 'https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}',
        street:    'https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png'
      };
      var attrs = { satellite: 'Google Satellite Hybrid', street: 'CartoDB Voyager' };
      var current = null;
      var btns = {};

      function switchTile(mode) {
        var mapEl = map.getContainer();
        var prevMode = _lsGet(LS_TILE, null);
        _ensureWindyFrame(mapEl);
        // ── Disable/enable zoom buttons based on tile mode ─────────────────────
        var zoomIn  = mapEl.querySelector('.leaflet-control-zoom-in');
        var zoomOut = mapEl.querySelector('.leaflet-control-zoom-out');
        var isWindy = (mode === 'windy');
        if (zoomIn)  { zoomIn.style.opacity  = isWindy ? '0.35' : '1'; zoomIn.style.pointerEvents  = isWindy ? 'none' : 'auto'; zoomIn.style.cursor  = isWindy ? 'not-allowed' : ''; }
        if (zoomOut) { zoomOut.style.opacity = isWindy ? '0.35' : '1'; zoomOut.style.pointerEvents = isWindy ? 'none' : 'auto'; zoomOut.style.cursor = isWindy ? 'not-allowed' : ''; }
        if (mode === 'windy') {
          var c = map.getCenter();
          var z = map.getZoom();
          var needSync = (prevMode !== 'windy') || (_lsGet(LS_W_LAT, null) === null);
          if (needSync) { window.flyWindy(c.lat, c.lng, z); }
          if (current) { map.removeLayer(current); current = null; }
          _windyFrame.style.display = 'block';
        } else {
          if (_windyFrame) _windyFrame.style.display = 'none';
          if (current) { map.removeLayer(current); }
          current = L.tileLayer(tiles[mode], { attribution: attrs[mode], maxZoom: 19 });
          current.addTo(map);
        }
        _lsSet(LS_TILE, mode);
        Object.keys(btns).forEach(function(k){
          btns[k].style.background = (k === mode) ? '#3b82f6' : 'transparent';
          btns[k].style.color      = (k === mode) ? '#ffffff' : '#94a3b8';
        });
      }

      ['windy','satellite','street'].forEach(function(mode){
        var btn = L.DomUtil.create('button', '', tileRow);
        btn.textContent = mode === 'windy' ? 'Windy'
                        : mode.charAt(0).toUpperCase() + mode.slice(1);
        btn.style.cssText = 'border:none;cursor:pointer;border-radius:5px;'
          + 'padding:3px 10px;font-size:12px;font-weight:600;'
          + 'transition:background 0.2s,color 0.2s;background:transparent;color:#94a3b8;';
        btns[mode] = btn;
        L.DomEvent.on(btn, 'click', function(){ switchTile(mode); });
      });

      map.whenReady(function(){
        var saved = _lsGet(LS_TILE, 'windy');
        if (saved !== 'satellite' && saved !== 'street' && saved !== 'windy') saved = 'windy';
        switchTile(saved);
      });

      return col;
    }
  });
  new CombinedCtrl().addTo({{ this._parent.get_name() }});
})();
{% endmacro %}
""")

class _CombinedControl(MacroElement):
    def __init__(self, lpm_url, location_name, initial_tile="windy"):
        super().__init__()
        self._name = '_CombinedControl'
        self._template = _COMBINED_CTRL_TEMPLATE
        self.lpm_url = lpm_url
        self.location_name = location_name
        self.initial_tile = initial_tile

# ── COMBINED CONTROL (Label/LPM on top, Tile switcher below, gap=6px) ─────────
_CombinedControl(
    lpm_url=_lpm_url,
    location_name=_strip_loc_num(st.session_state.location_name),
    initial_tile=st.session_state.map_tile,
).add_to(m)

# ── SEARCH CONTROL — inject location list vào JS, nằm topleft trên map ──────
import json as _json

# ── KANJI ⇄ ROMAJI ALIAS TABLE ───────────────────────────────────────────────
# Cho phép search bằng kanji (vd "福島", "秋元") match với tên romaji trong entry
# (vd "Fukushima", "Akimoto"). Mỗi entry sẽ được gắn thêm "alias text" chứa tất
# cả romaji keyword tương ứng với kanji xuất hiện trong tên.
_KANJI_ALIAS = {
    # ── 47 tỉnh (Prefectures) ────────────────────────────────────────────────
    "北海道": "Hokkaido", "青森": "Aomori", "岩手": "Iwate", "宮城": "Miyagi",
    "秋田": "Akita", "山形": "Yamagata", "福島": "Fukushima", "茨城": "Ibaraki",
    "栃木": "Tochigi", "群馬": "Gunma", "埼玉": "Saitama", "千葉": "Chiba",
    "東京": "Tokyo", "神奈川": "Kanagawa", "新潟": "Niigata", "富山": "Toyama",
    "石川": "Ishikawa", "福井": "Fukui", "山梨": "Yamanashi", "長野": "Nagano",
    "岐阜": "Gifu", "静岡": "Shizuoka", "愛知": "Aichi", "三重": "Mie",
    "滋賀": "Shiga", "京都": "Kyoto", "大阪": "Osaka", "兵庫": "Hyogo",
    "奈良": "Nara", "和歌山": "Wakayama", "鳥取": "Tottori", "島根": "Shimane",
    "岡山": "Okayama", "広島": "Hiroshima", "山口": "Yamaguchi", "徳島": "Tokushima",
    "香川": "Kagawa", "愛媛": "Ehime", "高知": "Kochi", "福岡": "Fukuoka",
    "佐賀": "Saga", "長崎": "Nagasaki", "熊本": "Kumamoto", "大分": "Oita",
    "宮崎": "Miyazaki", "鹿児島": "Kagoshima", "沖縄": "Okinawa",
    # ── Landmark / địa danh kanji → romaji trong tên entry ───────────────────
    "馬の背": "Jogashima", "白浜": "Shirahama", "大波月": "Onjuku", "雀島": "Isumi",
    "真鶴": "Manazuru", "愛の鐘": "Cape Aiai", "千貫門": "Matsuzaki",
    "奥大井湖上": "Okuoikojo", "朝霧高原": "Asagiri Plateau", "御嶽山": "Ontake",
    "上高地": "Kamikochi", "燕山荘": "Enzan-so", "イルカ岩": "Enzan-so",
    "美ヶ原": "Utsukushihara", "渋峠": "Yugama Shibutoge", "上発知": "Sakura",
    "シダレザクラ": "Sakura", "湯ノ湖": "Oku-Nikko", "天地人橋": "Hoshinomura",
    "浄土平": "Azuma-kofuji", "御釜": "Okama Zao", "東滑川": "Higashinamekawa",
    "奥多摩湖": "Okutama", "犬吠埼": "Choshi Inubosaki", "九十九里浜": "Kujukuri Beach",
    "安房白浜": "Awa Shirahama", "神磯の鳥居": "Oarai Isosaki", "袋田の滝": "Fukuroda Falls",
    "プラトーさとみ": "Plateau Satomi", "尾瀬ヶ原": "Oze Numata", "玉原高原": "Tanbara Highlands",
    "三十槌氷柱": "Chichibu Misotsuchi", "中津峡": "Nakatsu Gorge", "前浜海岸": "Kozushima Maehama",
    "御蔵島": "Mikurajima Observatory", "南原千畳岩": "Hachijojima Nambara",
    "山中湖": "Yamanakako Panorama", "清泉寮": "Kiyosato Seisenryo", "御坂峠": "Misaka Pass",
    "野辺山": "Nobeyama Radio Observatory", "高ボッチ高原": "Takabocchi Highlands",
    "曽爾高原": "Soni Highlands", "乗鞍畳平": "Norikura Tatamidaira", "平湯峠": "Hirayu Pass",
    "新穂高": "Shinhotaka Ropeway", "白川郷": "Shirakawago", "千里浜": "Chirihama Beach",
    "三方五湖": "Mikatagoko Rainbow Line", "鬼ヶ城": "Kumano Oni-ga-jo", "大王崎": "Daiozaki Lighthouse",
    "大台ヶ原": "Odaigahara Driveway", "天川村": "Tenkawa Miroku Pass", "西はりま天文台": "Nishiharima Observatory",
    "美星天文台": "Bisei Observatory", "蒜山高原": "Hiruzen Highlands", "鳥取砂丘": "Tottori Sand Dunes",
    "三朝温泉": "Misasa Onsen", "秋吉台": "Akiyoshidai Karst", "四国カルスト": "Shikoku Karst",
    "足摺岬": "Ashizuri Cape", "佐多岬": "Sata Cape", "草千里ヶ浜": "Aso Kusasenri",
    "大観峰": "Daikanbo", "生月島": "Ikitsuki Island", "波戸岬": "Yobuko Cape Hado",
    "高千穂": "Amaterasu Railway", "都井岬": "Cape Toi", "開聞岳": "Kaimondake",
    "百合ヶ浜": "Yoron Island", "平久保崎": "Ishigaki Hirakubozaki", "玉取崎": "Tamatorizaki Observatory",
    "星砂の浜": "Iriomote Hoshizuna Beach", "波照間島": "Hateruma Observatory", "残波岬": "Cape Zanpa",
    "古宇利大橋": "Kouri Bridge", "辺戸岬": "Cape Hedo", "東平安名崎": "Miyakojima Higashi-Hennazaki",
    "来間大橋": "Kurima Bridge", "青ヶ島": "Aogashima Observatory", "羽伏浦海岸": "Niijima Habushiura",
    "泊海岸": "Shikinejima Tomari Beach", "小笠原": "Ogasawara Weather Station",
    "霧ヶ峰": "Kirigamine Highlands", "白駒池": "Shirakoma Pond", "八千穂高原": "Yachiho Plateau",
    "千畳敷カール": "Senjojiki Cirque", "八方池": "Happo Pond", "栂池自然園": "Tsugaike Nature Park",
    "白馬岩岳": "Hakuba Iwatake", "志賀高原": "Shiga Highlands", "妙高高原": "Mt. Myoko",
    "弥彦山": "Yahiko Skyline", "瀬波海岸": "Senami Coast", "月山八合目": "Gassan Hachigome",
    "鳥海山": "Toriumi Observatory", "龍飛崎": "Cape Tappi", "能取岬": "Cape Notoro",
    "摩周湖": "Lake Mashu", "美幌峠": "Bihoro Pass", "屈斜路湖": "Lake Kussharo",
    "霧多布岬": "Cape Kiritappu", "襟裳岬": "Cape Erimo", "野付半島": "Notsuke Peninsula",
    "サロマ湖": "Lake Saroma", "知床峠": "Shiretoko Pass", "神威岬": "Cape Kamui",
    "大間崎": "Omazaki", "仏ヶ浦": "Hotokegaura", "十和田湖": "Lake Towada",
    "八甲田山": "Hakkoda", "乳頭温泉郷": "Nyuto Onsen", "田沢湖": "Tazawako",
    "入道崎": "Oga Nyudozaki", "浄土ヶ浜": "Jodogahama", "北山崎": "Kitayamazaki",
    "龍泉洞": "Ryusendo", "鳴子峡": "Naruko Gorge", "伊豆沼": "Izunuma",
    "羽黒山": "Mt. Haguro", "蔵王御釜": "Zao Okama", "只見線第一橋梁": "Tadami Bridge",
    "五色沼": "Goshikinuma", "猪苗代湖": "Inawashiro Lake", "雨晴海岸": "Amaharashi Coast",
    "室堂": "Tateyama Murodo", "庄川峡": "Shogawa Gorge", "見附島": "Mitsukejima",
    "白米千枚田": "Senmaida", "禄剛崎": "Rokkozaki", "白川八幡神社": "Shirakawa Hachiman",
    "恵那峡大橋": "Ena Ravine Bridge", "大望峠": "Daibo Pass", "乗鞍高原": "Norikura Kogen",
    "白馬大池": "Shirouma Oike", "野島崎": "Nojimazaki", "小弁天島": "Kobentenjima",
    "日御碕": "Izumo Hinomisaki", "宍道湖": "Lake Shinji", "橋杭岩": "Hashiguiiwa",
    "竹田城跡": "Takeda Castle", "伊根の舟屋": "Ine Funaya", "柏島": "Kashiwajima",
    "角島大橋": "Tsunoshima Bridge", "元乃隅神社": "Motonosumi Shrine", "父母ヶ浜": "Chichibugahama",
    "室戸岬": "Cape Muroto", "大内宿": "Ouchi-juku", "星峠の棚田": "Hoshitoge Rice Terraces",
    "桧原湖": "Lake Hibara", "尻屋崎": "Cape Shiriya", "小川原湖": "Lake Ogawara",
    "納沙布岬": "Cape Nosappu", "地球岬": "Cape Chikyu", "オンネトー": "Lake Onneto",
    "青い池": "Shirogane Blue Pond", "恵山岬": "Cape Esan", "黄金崎": "Koganezaki",
    "五箇山相倉集落": "Gokayama Ainokura", "三国峠": "Mikuni Pass", "奥入瀬渓流": "Oirase Stream",
    "種差海岸": "Tanesashi Coast", "蕪島神社": "Kabushima Shrine", "厳美渓": "Genbikei Gorge",
    "栗駒山": "Mt. Kurikoma", "秋元湖": "Lake Akimoto", "秋元": "Akimoto",
    "磐梯山": "Bandai-san", "磐梯": "Bandai",
    # ── Locations 101-250 (added in v5.80+) ────────────────────────────────
    # Hokkaido
    "能取": "Cape Notoro", "知床": "Shiretoko Pass", "野付": "Notsuke Peninsula",
    "サロマ": "Lake Saroma", "釧路湿原": "Akan Crane", "阿寒湖": "Lake Akan",
    "落石岬": "Cape Ochiishi", "洞爺湖": "Lake Toya", "登別地獄谷": "Noboribetsu Jigokudani",
    "青い池": "Shirogane Blue Pond", "三国峠": "Mikuni Pass",
    # Tohoku (101-174)
    "船形山": "Funagata-yama",
    # Ishikawa / Toyama / Fukui
    "白山": "Hakusan Chokaisanso", "雨晴": "Amaharashi Coast",
    "見附島": "Mitsukejima", "千枚田": "Senmaida", "禄剛": "Rokkozaki",
    "庄川峡": "Shogawa Gorge", "五箇山": "Gokayama Ainokura",
    "東尋坊": "Tojinbo", "永平寺": "Eiheiji Temple",
    # Nagano (additional)
    "大望峠": "Daibo Pass", "乗鞍高原": "Norikura Kogen", "白馬大池": "Shirouma Oike",
    "野島崎": "Nojimazaki",
    # Shimane / Tottori / Okayama / Hiroshima
    "日御碕": "Izumo Hinomisaki", "仁摩": "Nima Sand Museum",
    "出雲大社": "Izumo Taisha", "足立美術館": "Adachi Museum", "隠岐": "Oki Islands",
    "大山": "Tottori Daisen", "蒜山": "Hiruzen Highlands",
    "鞆の浦": "Tomonoura", "三段峡": "Sandankyo Gorge", "大久野島": "Okunoshima",
    "三谷峡": "Mitani Valley",
    # Wakayama / Mie / Nara
    "潮岬": "Shionomisaki Cape", "那智の滝": "Nachi Falls",
    "三段壁": "Sandanbeki", "高野山": "Mt. Koya",
    "伊勢神宮": "Ise Jingu",
    # Kyoto / Hyogo
    "成相寺": "Nariai-ji Temple", "天橋立": "Amanohashidate",
    "久美浜": "Kumihama Bay", "城崎": "Kinosaki Onsen",
    "姫路城": "Himeji Castle", "明石海峡大橋": "Akashi Kaikyo Bridge",
    # Shiga / Gifu
    "琵琶湖": "Lake Biwa Terrace", "彦根城": "Hikone Castle",
    "郡上八幡": "Gujo Hachiman", "馬籠宿": "Magome-juku",
    # Kagawa / Tokushima / Ehime / Kochi
    "父母ヶ浜": "Chichibugahama", "金刀比羅宮": "Kotohira-gu",
    "大歩危峡": "Oboke Gorge", "祖谷": "Iya Valley",
    "石鎚山": "Mt. Ishizuchi", "道後温泉": "Dogo Onsen", "佐田岬": "Sadamisaki Peninsula",
    "室戸ジオパーク": "Muroto Geopark", "桂浜": "Katsurahama Beach",
    "足摺": "Ashizuri Cape", "四万十": "Shimanto River",
    # Yamaguchi / Kyushu
    "角島大橋": "Tsunoshima Bridge", "元乃隅": "Motonosumi Shrine",
    "秋吉台": "Akiyoshidai Karst", "錦帯橋": "Kintaikyo Bridge",
    "太宰府": "Dazaifu Tenmangu", "唐津城": "Karatsu Castle",
    "吉野ヶ里": "Yoshinogari", "グラバー園": "Nagasaki Glover",
    "久住高原": "Kuju Highlands",
    "熊本城": "Kumamoto Castle", "臼杵石仏": "Usuki Stone Buddhas",
    "別府地獄": "Beppu Hells", "高千穂峡": "Takachiho Gorge",
    "都井岬": "Cape Toi", "桜島溶岩": "Sakurajima",
    "霧島神宮": "Kirishima Shrine", "屋久島": "Yakushima",
    "奄美大島": "Amami Oshima",
    # Okinawa
    "首里城": "Shuri Castle", "斎場御嶽": "Sefa-utaki",
    "万座毛": "Cape Manzamo", "中城城": "Nakagusuku Castle",
    "勝連城": "Katsuren Castle", "座喜味城": "Zakimi Castle",
    "真栄田岬": "Cape Maeda", "慶良間": "Kerama Islands",
    "ジャングル": "Iriomote Jungle",

    # ── Alternate / common place names (tên gọi phổ biến khác của địa danh) ──
    "城ヶ島": "Jogashima", "伊豆大島": "Izu Oshima", "三浦半島": "Manazuru",
    "富士山": "Fuji", "富士五湖": "Fuji Five Lakes", "河口湖": "Kawaguchiko",
    "野尻湖": "Nojiriko", "美ヶ原高原": "Utsukushihara", "霧ヶ峰高原": "Kirigamine Highlands",
    "白馬村": "Hakuba", "蓼科": "Tateshina", "車山": "Kurumayama",
    "陽明門": "Oku-Nikko", "中禅寺湖": "Oku-Nikko", "華厳の滝": "Oku-Nikko",
    "知床": "Shiretoko Pass", "摩周": "Lake Mashu", "屈斜路": "Lake Kussharo",
    "阿蘇": "Aso Kusasenri", "霧島": "Kaimondake", "桜島": "Kagoshima",
    "石垣島": "Ishigaki Hirakubozaki", "宮古島": "Miyakojima Higashi-Hennazaki",
    "石垣": "Ishigaki Hirakubozaki", "宮古": "Miyakojima Higashi-Hennazaki",
    "西表島": "Iriomote Hoshizuna Beach", "波照間": "Hateruma Observatory",
    "与論島": "Yoron Island", "屋久島": "Kagoshima", "種子島": "Kagoshima",
    "礪波": "Shogawa Gorge", "五箇山": "Gokayama Ainokura", "白川村": "Shirakawago",
    "恵那峡": "Ena Ravine Bridge", "高山": "Hirayu Pass", "奥飛騨": "Hirayu Pass",
    "天橋立": "Ine Funaya", "丹後": "Ine Funaya", "下田": "Shimoda",
    "南伊豆": "Cape Aiai", "石廊崎": "Cape Aiai", "西伊豆": "Koganezaki",
    "鳥羽": "Daiozaki Lighthouse", "志摩": "Daiozaki Lighthouse",
    "天草": "Amaterasu Railway", "由布岳": "Hiruzen Highlands",
    # ── Locations 251-266 ────────────────────────────────────────────────────
    "いすみ鉄道": "Isumi Railway Crossing", "第二五之町踏切": "Isumi Railway Crossing",
    "大山千枚田": "Oyama Senmaida", "東浪見の鳥居": "Tonami no Torii",
    "あさひ舟川": "Asahi Funakawa", "春の四重奏": "Asahi Funakawa",
    "真脇遺跡": "Mawaki Ruins", "星の観察館": "Hoshi no Kanrankan",
    "白山展望台": "Hakusan Tenbodai",
    "鹿角平": "Shikanotsuno Observatory", "郡山布引": "Koriyama Nunobiki Wind Farm",
    "磐梯山眺望": "Bandaisan Viewpoint", "かねやまふれあい": "Kaneyama Fureai Hiroba",
    "上野スカイブリッジ": "Ueno Sky Bridge", "くらぶちこども天文台": "Kurabuchi Children Observatory",
    "神津牧場天文台": "Kozumaki Ranch Observatory", "高根展望台": "Takane Observatory",
    "奥只見ダム": "Okutadami Dam",
}

_loc_js_list = _json.dumps([
    {"name": name, "lat": coords[0], "lon": coords[1]}
    for name, coords in LOCATION_DATABASE.items()
])
_kanji_alias_js = _json.dumps(_KANJI_ALIAS, ensure_ascii=False)




_SEARCH_CTRL_TEMPLATE = Template("""
{% macro script(this, kwargs) %}
(function(){
  var _DB = {{ this.loc_list }};
  var _ALIAS = {{ this.alias_dict }};

  var SearchCtrl = L.Control.extend({
    options: { position: 'topleft' },
    onAdd: function(map) {
      var wrapper = L.DomUtil.create('div', '');
      wrapper.style.cssText = 'position:relative;';
      L.DomEvent.disableClickPropagation(wrapper);
      L.DomEvent.disableScrollPropagation(wrapper);

      // ── Container row ──────────────────────────────────────────────────────
      var row = L.DomUtil.create('div', '', wrapper);
      row.style.cssText = (
        'display:flex;align-items:center;gap:4px;'
        + 'background:rgba(15,23,42,0.92);border:1px solid #334155;'
        + 'border-radius:8px;padding:4px 7px;box-shadow:0 2px 8px rgba(0,0,0,0.6);'
      );

      // ── Search icon ────────────────────────────────────────────────────────
      var icon = L.DomUtil.create('span', '', row);
      icon.innerHTML = '&#128269;';
      icon.style.cssText = 'font-size:14px;cursor:pointer;color:#94a3b8;line-height:1;flex-shrink:0;';

      // ── Input ──────────────────────────────────────────────────────────────
      var inp = L.DomUtil.create('input', '', row);
      inp.type = 'text';
      inp.placeholder = 'Search location…';
      inp.style.cssText = (
        'background:transparent;border:none;outline:none;'
        + 'color:#e2e8f0;font-size:12px;width:180px;'
        + 'font-family:sans-serif;padding:0;'
      );

      // ── Clear button ───────────────────────────────────────────────────────
      var clr = L.DomUtil.create('span', '', row);
      clr.innerHTML = '&#10005;';
      clr.style.cssText = 'font-size:11px;cursor:pointer;color:#64748b;display:none;flex-shrink:0;';
      L.DomEvent.on(clr, 'click', function(){
        inp.value = '';
        clr.style.display = 'none';
        dropdown.style.display = 'none';
        inp.focus();
      });

      // ── Dropdown ───────────────────────────────────────────────────────────
      var dropdown = L.DomUtil.create('div', '', wrapper);
      dropdown.style.cssText = (
        'position:absolute;top:36px;left:0;z-index:9999;'
        + 'background:rgba(15,23,42,0.97);border:1px solid #334155;'
        + 'border-radius:8px;box-shadow:0 4px 16px rgba(0,0,0,0.7);'
        + 'max-height:400px;overflow-y:auto;min-width:260px;display:none;'
      );

      var _activeIdx = -1;
      var _items = [];

      function _highlight(idx) {
        _items.forEach(function(el, i){
          el.style.background = (i === idx) ? 'rgba(59,130,246,0.35)' : '';
        });
        _activeIdx = idx;
      }

      function _selectItem(item) {
        inp.value = item.name;
        dropdown.style.display = 'none';
        clr.style.display = 'inline';
        map.setView([item.lat, item.lon], 11, {animate:true, duration:0.8});
        // Fly Windy to same location
        if (typeof window.flyWindy === 'function') {
          window.flyWindy(item.lat, item.lon, 8);
        }
        // Fire synthetic click so Python receives last_clicked and updates session state.
        // Delay 900ms to let map animation finish first.
        setTimeout(function(){
          map.fire('click', { latlng: L.latLng(item.lat, item.lon) });
        }, 900);
      }

      function _buildDropdown(results, isTopList) {
        isTopList = !!isTopList;
        dropdown.innerHTML = '';
        _items = [];
        _activeIdx = -1;
        if (results.length === 0) {
          var empty = L.DomUtil.create('div', '', dropdown);
          empty.style.cssText = 'padding:10px 14px;color:#64748b;font-size:12px;';
          empty.textContent = 'No match — press Enter to geocode';
          dropdown.style.display = 'block';
          return;
        }
        // Header label
        var hdr = L.DomUtil.create('div', '', dropdown);
        hdr.style.cssText = 'padding:5px 14px 3px;font-size:10px;color:#475569;'
          + 'font-weight:700;letter-spacing:0.05em;text-transform:uppercase;'
          + 'border-bottom:1px solid rgba(51,65,85,0.5);';
        hdr.textContent = isTopList ? 'All locations (' + _DB.length + ')' : 'Results';
        results.slice(0, isTopList ? _DB.length : 30).forEach(function(item, i) {
          var el = L.DomUtil.create('div', '', dropdown);
          el.style.cssText = (
            'padding:7px 14px;cursor:pointer;font-size:12px;'
            + 'color:#cbd5e1;border-bottom:1px solid rgba(51,65,85,0.4);'
            + 'white-space:nowrap;overflow:hidden;text-overflow:ellipsis;'
          );
          el.title = item.name;
          // Strip number prefix for display
          var cleanName = item.name.replace(/^\d+\.\s*/, '');
          el.textContent = cleanName;
          _items.push(el);
          L.DomEvent.on(el, 'click', function(){ _selectItem(item); });
          L.DomEvent.on(el, 'mouseover', function(){ _highlight(i); });
        });
        dropdown.style.display = 'block';
      }

      // ── Geocode fallback via Nominatim ─────────────────────────────────────
      function _geocodeAndFly(query) {
        var url = 'https://nominatim.openstreetmap.org/search?format=json&q='
          + encodeURIComponent(query) + '&limit=1';
        fetch(url, { headers: { 'User-Agent': 'AstroMapPro/7.0' }})
          .then(function(r){ return r.json(); })
          .then(function(data){
            if (data && data.length > 0) {
              var lat = parseFloat(data[0].lat);
              var lon = parseFloat(data[0].lon);
              map.setView([lat, lon], 11, {animate:true, duration:0.8});
              // Fly Windy to geocoded location
              if (typeof window.flyWindy === 'function') {
                window.flyWindy(lat, lon, 8);
              }
              dropdown.innerHTML = '';
              var found = L.DomUtil.create('div', '', dropdown);
              found.style.cssText = 'padding:8px 14px;font-size:12px;color:#34d399;';
              found.textContent = data[0].display_name;
              found.innerHTML = '&#128205; ' + data[0].display_name;
              dropdown.style.display = 'block';
              setTimeout(function(){
                map.fire('click', { latlng: L.latLng(lat, lon) });
              }, 900);
            } else {
              dropdown.innerHTML = '';
              var nf = L.DomUtil.create('div', '', dropdown);
              nf.style.cssText = 'padding:8px 14px;font-size:12px;color:#f87171;';
              nf.textContent = 'Location not found';
              dropdown.style.display = 'block';
            }
          })
          .catch(function(){
            dropdown.innerHTML = '';
            var err = L.DomUtil.create('div', '', dropdown);
            err.style.cssText = 'padding:8px 14px;font-size:12px;color:#f87171;';
            err.textContent = 'Geocoding error';
            dropdown.style.display = 'block';
          });
      }

      // ── Input events ───────────────────────────────────────────────────────
      // Show all locations on focus (when input is empty)
      L.DomEvent.on(inp, 'focus', function(){
        if (inp.value.trim() === '') {
          _buildDropdown(_DB, true);
        }
      });

      L.DomEvent.on(inp, 'blur', function(){
        // Slight delay so click on dropdown item fires first
        setTimeout(function(){
          if (inp.value.trim() === '') {
            dropdown.style.display = 'none';
          }
        }, 200);
      });

      L.DomEvent.on(inp, 'input', function(){
        var qRaw = inp.value.trim();
        var q = qRaw.toLowerCase();
        clr.style.display = q ? 'inline' : 'none';
        if (!q) { dropdown.style.display = 'none'; return; }
        // Hidden keyword — show subtle hint in dropdown, do not search DB
        if (q === 'scan') {
          dropdown.innerHTML = '';
          var hint = L.DomUtil.create('div', '', dropdown);
          hint.style.cssText = 'padding:8px 14px;font-size:12px;color:#34d399;';
          hint.textContent = 'Press Enter to scan for great nights…';
          dropdown.style.display = 'block';
          return;
        }

        // Translate any kanji substrings in the query to their romaji alias
        var translations = [];
        for (var kanji in _ALIAS) {
          if (qRaw.indexOf(kanji) !== -1) {
            translations.push(_ALIAS[kanji].toLowerCase());
          }
        }

        var results = _DB.filter(function(item){
          var nl = item.name.toLowerCase();
          if (nl.indexOf(q) !== -1) return true;
          for (var i = 0; i < translations.length; i++) {
            if (nl.indexOf(translations[i]) !== -1) return true;
          }
          return false;
        });
        _buildDropdown(results);
      });

      L.DomEvent.on(inp, 'keydown', function(e){
        if (e.key === 'Enter') {
          e.preventDefault();
          // ── Hidden SCAN trigger: gõ "scan" + Enter ──────────────────────────
          if (inp.value.trim().toLowerCase() === 'scan') {
            inp.value = '';
            clr.style.display = 'none';
            dropdown.style.display = 'none';
            if (typeof window._triggerScan === 'function') window._triggerScan();
            return;
          }
          if (dropdown.style.display === 'none') return;
          if (_activeIdx >= 0 && _activeIdx < _items.length) {
            _items[_activeIdx].click();
          } else {
            dropdown.style.display = 'none';
            _geocodeAndFly(inp.value.trim());
          }
          return;
        }
        if (dropdown.style.display === 'none') return;
        if (e.key === 'ArrowDown') {
          e.preventDefault();
          _highlight(Math.min(_activeIdx + 1, _items.length - 1));
          if (_items[_activeIdx]) _items[_activeIdx].scrollIntoView({block:'nearest'});
        } else if (e.key === 'ArrowUp') {
          e.preventDefault();
          _highlight(Math.max(_activeIdx - 1, 0));
          if (_items[_activeIdx]) _items[_activeIdx].scrollIntoView({block:'nearest'});
        } else if (e.key === 'Escape') {
          dropdown.style.display = 'none';
        }
      });

      // Close dropdown when clicking outside
      map.on('click', function(){ dropdown.style.display = 'none'; });

      return wrapper;
    }
  });
  new SearchCtrl().addTo({{ this._parent.get_name() }});
})();
{% endmacro %}
""")

class _SearchControl(MacroElement):
    def __init__(self, loc_list="[]", alias_dict="{}"):
        super().__init__()
        self._name = '_SearchControl'
        self._template = _SEARCH_CTRL_TEMPLATE
        self.loc_list = loc_list
        self.alias_dict = alias_dict

_SearchControl(loc_list=_loc_js_list, alias_dict=_kanji_alias_js).add_to(m)

# ── CSS cho tooltip (hover) ────────────────────────────────────────────────────
m.get_root().html.add_child(folium.Element("""
<style>
.leaflet-tooltip {
    background: white !important;
    border: 1px solid #cbd5e1 !important;
    border-radius: 8px !important;
    box-shadow: 0 4px 12px rgba(0,0,0,0.25) !important;
    padding: 6px !important;
    max-width: 240px !important;
}
.leaflet-tooltip::before { display: none !important; }
.leaflet-control-attribution { display: none !important; }
</style>
"""))

# ── LOCATION MARKERS ──────────────────────────────────────────────────────────
import os, base64

def _get_loc_image_b64(loc_name: str):
    """Tìm ảnh theo số thứ tự ở đầu tên địa danh (vd: '23. Hoshinomura...' → tìm images/23.*).
    Trả về (base64_string, mime_type) hoặc (None, None) nếu không tìm thấy."""
    num = loc_name.split(".")[0].strip()
    img_dir = os.path.join(os.path.dirname(__file__), "images")
    if not os.path.isdir(img_dir):
        return None, None
    for ext, mime in [("jpg","image/jpeg"),("jpeg","image/jpeg"),("png","image/png"),("webp","image/webp")]:
        path = os.path.join(img_dir, f"{num}.{ext}")
        if os.path.isfile(path):
            with open(path, "rb") as f:
                return base64.b64encode(f.read()).decode(), mime
    return None, None

_selected_marker_args = None  # lưu lại marker được chọn, vẽ sau cùng để nổi lên trên

for loc_name, loc_coords in LOCATION_DATABASE.items():
    is_sel = abs(loc_coords[0]-st.session_state.lat)<0.001 and abs(loc_coords[1]-st.session_state.lon)<0.001
    try:
        loc_num = int(loc_name.split(".")[0].strip())
    except ValueError:
        loc_num = 99
    is_frequent = (loc_num <= 27)
    if is_sel:
        star_color = "#00FFFF" if is_frequent else "#FFD700"
        star_glow  = "drop-shadow(0 0 7px cyan)" if is_frequent else "drop-shadow(0 0 6px gold)"
        star_size  = "22px"
    else:
        star_color = "#22D3EE" if is_frequent else "#FFA500"
        star_glow  = "none"
        star_size  = "16px"
    b64, mime = _get_loc_image_b64(loc_name)
    if b64:
        img_html = (f'<img src="data:{mime};base64,{b64}" '
                    f'style="width:220px;max-height:150px;object-fit:cover;border-radius:6px;'
                    f'display:block;margin-bottom:6px;">')
    else:
        img_html = ""
    _loc_label = _strip_loc_num(loc_name)
    _label_fs = 13 if len(_loc_label) <= 28 else (11 if len(_loc_label) <= 38 else 9.5)
    tooltip_html = (f'<div style="font-family:sans-serif;font-size:{_label_fs}px;font-weight:600;'
                    f'color:#1e293b;max-width:230px;line-height:1.35;'
                    f'white-space:normal;word-break:break-word;overflow-wrap:break-word;">'
                    f'{img_html}{_loc_label}</div>')
    if is_sel:
        # Ngôi sao được chọn: nhấp nháy (pulse) để dễ nhận biết + z-index cao để
        # không bị các ngôi sao khác che mất khi zoom nhỏ.
        _star_html = (
            f'<style>@keyframes star-pulse-sel {{'
            f'0%,100%{{transform:scale(1);opacity:1;}}'
            f'50%{{transform:scale(1.35);opacity:0.55;}}}}</style>'
            f'<div style="font-size:{star_size};color:{star_color};'
            f'text-shadow:0 0 4px rgba(0,0,0,0.9);filter:{star_glow};'
            f'cursor:pointer;line-height:1;font-family:serif;'
            f'animation:star-pulse-sel 1.1s ease-in-out infinite;'
            f'transform-origin:center;display:inline-block;'
            f'position:relative;z-index:10000;">★</div>'
        )
        # Lưu lại, vẽ sau cùng (sau loop) để marker này nằm trên cùng DOM stack
        _selected_marker_args = (loc_coords, _star_html, tooltip_html)
        continue
    else:
        _star_html = (
            f'<div style="font-size:{star_size};color:{star_color};'
            f'text-shadow:0 0 4px rgba(0,0,0,0.9);filter:{star_glow};'
            f'cursor:pointer;line-height:1;font-family:serif;">★</div>'
        )
    folium.Marker(
        loc_coords,
        icon=folium.DivIcon(
            html=_star_html,
            icon_size=(24,24), icon_anchor=(12,12)),
        tooltip=folium.Tooltip(tooltip_html, sticky=False, offset=(20, -10), parse_html=False),
    ).add_to(m)

# ── Vẽ marker được chọn SAU CÙNG → nằm trên cùng trong DOM stack của Leaflet ──
# Leaflet gắn className của DivIcon trực tiếp lên thẻ .leaflet-marker-icon (chính
# thẻ có inline z-index do Leaflet tự set theo vị trí lat). Dùng class riêng +
# CSS !important để ép z-index của marker được chọn luôn cao nhất, không bị
# các sao khác (kể cả ở lat thấp hơn → z-index Leaflet cao hơn) che mất.
if _selected_marker_args:
    _sel_coords, _sel_html, _sel_tooltip = _selected_marker_args
    m.get_root().html.add_child(folium.Element("""
        <style>
            .selected-star-marker { z-index: 999999 !important; }
        </style>
    """))
    folium.Marker(
        _sel_coords,
        icon=folium.DivIcon(
            html=_sel_html,
            icon_size=(24,24), icon_anchor=(12,12),
            class_name="selected-star-marker"),
        tooltip=folium.Tooltip(_sel_tooltip, sticky=False, offset=(20, -10), parse_html=False),
    ).add_to(m)

is_bookmark = any(abs(c[0]-st.session_state.lat)<0.001 and abs(c[1]-st.session_state.lon)<0.001
                  for c in LOCATION_DATABASE.values())

# ── GREAT NIGHT SCAN result — vòng tròn nhấp nháy quanh tất cả địa điểm ──────
# Kích thước cố định theo pixel (DivIcon) → không thay đổi khi zoom in/out.
_scan_r = st.session_state._scan_result
if _scan_r and _scan_r != "none":
    _ring_css = (
        '<style>@keyframes great-night-pulse {'
        '0%{transform:scale(0.6);opacity:0.9;}'
        '70%{transform:scale(2.2);opacity:0;}'
        '100%{transform:scale(0.6);opacity:0;}}</style>'
    )
    _ring_body = (
        '<div style="width:64px;height:64px;border-radius:50%;'
        'border:3px solid #6ee7b7;'
        'box-shadow:0 0 14px rgba(110,231,183,0.8);'
        'animation:great-night-pulse 1.8s ease-out infinite;'
        'transform-origin:center;pointer-events:none;"></div>'
    )
    # Vẽ vòng tròn cho tất cả địa điểm trong all_locs (đã lọc <20km)
    _all_locs = _scan_r.get("all_locs", [(_scan_r["loc_name"], _scan_r["loc_coords"], _scan_r["verdict"])])
    for _i, (_aln, _alc, _alv) in enumerate(_all_locs):
        # Chỉ inject CSS 1 lần (marker đầu tiên)
        _ring_html = (_ring_css if _i == 0 else "") + _ring_body
        folium.Marker(
            list(_alc),
            icon=folium.DivIcon(html=_ring_html, icon_size=(64,64), icon_anchor=(32,32)),
        ).add_to(m)

if not is_bookmark:
    folium.Marker(
        [st.session_state.lat, st.session_state.lon],
        icon=folium.DivIcon(
            html='<div style="font-size:28px;line-height:1;filter:drop-shadow(0 0 6px rgba(255,50,50,0.9));cursor:pointer;">📍</div>',
            icon_size=(32,32), icon_anchor=(10,30)),
        tooltip=folium.Tooltip(f"📍 {_strip_loc_num(st.session_state.location_name)}", sticky=True)
    ).add_to(m)

# ── st_folium ─────────────────────────────────────────────────────────────────
# QUAN TRỌNG: KHÔNG đưa "zoom"/"center" vào returned_objects.
# Nếu có → mỗi pan/zoom map trả data về Python → Streamlit rerun → map refresh.
# Chỉ return những gì cần xử lý click. Zoom/center được lưu qua _need_fly flag.
_map_key = "astro_map_main"
_stfolium_kwargs = dict(
    width='stretch', height=575, key=_map_key,
    returned_objects=["last_clicked", "last_object_clicked_tooltip"],
)
if st.session_state._need_fly:
    _stfolium_kwargs["center"] = st.session_state.map_center
    st.session_state._need_fly = False   # reset ngay — chỉ fly 1 lần
map_data = st_folium(m, **_stfolium_kwargs)

# ── TOP-CENTER MAP LABEL — NIGHT VERDICT (full night 18:00~06:00) ────────────
if st.session_state.day_offset == 0:
    (_full_table_data, _full_hours_labels, _full_moon_alt, _full_sun_alt, *_rest_full) = _build_night_data(
        st.session_state.lat, st.session_state.lon,
        tuple(_full_night_slots),
        _hourly_frozen,
        st.session_state.weather_source,
        loc_utc_offset_h,
    )
    _verdict = _build_night_verdict(_full_table_data, _full_sun_alt, moon_pct)
else:
    _verdict = _build_night_verdict(weather_table_data, sun_altitudes, moon_pct)
if _verdict:
    # ── Tính nhiệt độ min/max của đêm (18:00~06:00) ──────────────────────────
    if st.session_state.day_offset == 0:
        _temp_src_table = _full_table_data
    else:
        _temp_src_table = weather_table_data
    _night_temps = [r.get("_temp") for r in _temp_src_table[:12] if r.get("_temp") is not None]
    if _night_temps:
        _temp_range_str = f"{round(max(_night_temps))}°-{round(min(_night_temps))}°"
    else:
        _temp_range_str = ""

    # ── Date label: "Tonight" nếu day_offset=0, còn lại "MM/DD night(min°~max°)" ─
    if st.session_state.day_offset == 0:
        _date_label = f"Tonight{f' ({_temp_range_str})' if _temp_range_str else ''}"
    else:
        _date_label = f"{target_date.month}月{target_date.day}日夜{f'({_temp_range_str})' if _temp_range_str else ''}"

    _warn_speed = "1.1s" if _verdict["anim"] == "blink-warn" else "1.9s"
    _html_label = f"""
<style>
@keyframes blink-warn   {{0%,100%{{opacity:1}}50%{{opacity:0.25}}}}
@keyframes blink-smile  {{0%,100%{{opacity:1;transform:scale(1)}}50%{{opacity:0.80;transform:scale(1.05)}}}}
@keyframes blink-neutral{{0%,100%{{opacity:1}}50%{{opacity:0.55}}}}
.astro-maplabel{{
  position:absolute;top:40px;left:50%;transform:translateX(-50%);
  z-index:9999;pointer-events:none;
  display:inline-flex;flex-direction:column;align-items:center;gap:1px;
  padding:5px 18px 6px 14px;border-radius:22px;
  font-family:sans-serif;
  white-space:nowrap;
  box-shadow:0 2px 16px rgba(0,0,0,0.75);
  backdrop-filter:blur(3px);
  background:{_verdict["bg"]};border:1.5px solid {_verdict["border"]};color:{_verdict["color"]};
}}
.astro-maplabel-top{{ font-size:9px;opacity:0.55;font-weight:600;letter-spacing:0.04em;line-height:1.2; }}
.astro-maplabel-main{{ display:flex;align-items:center;gap:7px;font-size:13px;font-weight:700;line-height:1.3; }}
.astro-maplabel-stars{{ font-size:11px;opacity:0.85;letter-spacing:1px; }}
.astro-maplabel-sub{{ font-size:10px;opacity:0.65;font-weight:500; }}
</style>
<div style="position:relative;margin-top:-644px;height:0;overflow:visible;z-index:9999;">
<div class="astro-maplabel">
  <span class="astro-maplabel-top">{_date_label}</span>
  <div class="astro-maplabel-main">
    <span style="animation:{_verdict["anim"]} {_warn_speed} ease-in-out infinite;display:inline-block;font-size:17px;">{_verdict["icon"]}</span>
    <span>{_verdict["tier"]}</span>
    <span class="astro-maplabel-stars">{_verdict["stars"]}</span>
    <span class="astro-maplabel-sub">{_verdict["sub"]}</span>
  </div>
</div>
</div>"""
    st.markdown(_html_label, unsafe_allow_html=True)

# ── BOTTOM-LEFT MAP OVERLAY — GREAT NIGHT SCAN RESULT ────────────────────────
_scan_r2 = st.session_state._scan_result
if _scan_r2 and _scan_r2 != "none":
    _sr_date2      = _scan_r2["date"]
    _sr_loc_label2 = _scan_r2["loc_name"]
    _all_locs2     = _scan_r2.get("all_locs", [(_scan_r2["loc_name"], _scan_r2["loc_coords"], _scan_r2["verdict"])])
    _n_spots       = len(_all_locs2)
    if _n_spots > 1:
        _spots_line = f'<div style="font-size:10.5px;opacity:0.70;margin-top:1px;">+ {_n_spots - 1} more spot{"s" if _n_spots > 2 else ""} — see rings on map</div>'
    else:
        _spots_line = ""
    _scan_banner_html = f"""
<div style="position:relative;margin-top:-644px;height:0;overflow:visible;z-index:9998;">
<div style="
  position:absolute;bottom:14px;left:14px;max-width:340px;
  background:rgba(5,25,18,0.90);border:1.5px solid rgba(52,211,153,0.75);
  border-radius:10px;padding:8px 14px;
  font-family:sans-serif;color:#6ee7b7;
  box-shadow:0 2px 16px rgba(0,0,0,0.75);backdrop-filter:blur(3px);
  pointer-events:none;line-height:1.4;
">
  <div style="font-size:13px;font-weight:700;">🌌 {_sr_date2.month}/{_sr_date2.day} — PERFECT NIGHT</div>
  <div style="font-size:12px;font-weight:600;margin-top:2px;">at {_strip_loc_num(_sr_loc_label2)}</div>
  <div style="font-size:10.5px;opacity:0.75;margin-top:2px;">moon {_scan_r2['moon_illum']:.0f}%, {_scan_r2['verdict']['sub']}</div>
  {_spots_line}
</div>
</div>"""
    st.markdown(_scan_banner_html, unsafe_allow_html=True)
elif _scan_r2 == "none":
    _scan_banner_html = """
<div style="position:relative;margin-top:-644px;height:0;overflow:visible;z-index:9998;">
<div style="
  position:absolute;bottom:14px;left:14px;max-width:320px;
  background:rgba(10,14,22,0.88);border:1.5px solid rgba(148,163,184,0.55);
  border-radius:10px;padding:8px 14px;
  font-family:sans-serif;color:#94a3b8;
  box-shadow:0 2px 16px rgba(0,0,0,0.75);backdrop-filter:blur(3px);
  pointer-events:none;line-height:1.4;font-size:12px;font-weight:600;
">
  🔍 No PERFECT NIGHT in the next 7 days
</div>
</div>"""
    st.markdown(_scan_banner_html, unsafe_allow_html=True)

# ── LPM EXTERNAL LINK ─────────────────────────────────────────────────────────
# URL is used inline in the nav row beside the location selectbox
_lpm_url = (f"https://lightpollutionmap.app/"
            f"?lat={st.session_state.lat:.4f}&lng={st.session_state.lon:.4f}&zoom=10")

# ── MAP CLICK HANDLER ─────────────────────────────────────────────────────────
if map_data:
    clicked_tip = map_data.get("last_object_clicked_tooltip")
    lc          = map_data.get("last_clicked")

    # ── Priority 0: SCAN button (sentinel click at lat=99.9, lon=99.9) ────────
    if lc and lc != st.session_state._last_lc and abs(lc.get("lat", 0) - 99.9) < 0.01 and abs(lc.get("lng", 0) - 99.9) < 0.01:
        st.session_state._last_lc = lc
        with st.spinner("Scanning 27 favorite spots over the next 7 nights..."):
            _scan_res = _run_great_night_scan()
        st.session_state._scan_result = _scan_res if _scan_res is not None else "none"
        st.rerun()

    # ── Priority 1: star marker click (via tooltip) ───────────────────────────
    # last_clicked luôn NULL với DivIcon, chỉ dùng tooltip để detect click ngôi sao.
    # Tooltip HTML chỉ chứa _strip_loc_num(bname) → match theo tên stripped.
    if clicked_tip:
        matched = None
        tip_str = str(clicked_tip)
        for bname, bcoords in LOCATION_DATABASE.items():
            stripped = _strip_loc_num(bname)
            if stripped in tip_str:
                matched = (bname, bcoords)
                break
        if matched:
            bname, bcoords = matched
            _tip_key = f"{bcoords[0]:.4f},{bcoords[1]:.4f}"
            if _tip_key != st.session_state._last_tip:
                # Nếu click sao mới → xử lý và lưu key để chặn rerun kép
                # Nếu click lại cùng sao → _tip_key == _last_tip → skip (không cần rerun)
                st.session_state._last_tip       = _tip_key
                st.session_state._last_lc        = lc
                st.session_state.lat             = bcoords[0]
                st.session_state.lon             = bcoords[1]
                st.session_state.map_center      = [bcoords[0], bcoords[1]]
                st.session_state.location_name   = bname
                st.session_state.is_custom_point = False
                st.session_state._need_fly       = False
                st.session_state.day_offset      = 0
                st.session_state._skip_prefetch  = True
                st.session_state.sel_date        = date_options[0]
                st.rerun()
        else:
            # Tooltip không match sao nào → reset để lần sau click cùng sao vẫn work
            st.session_state._last_tip = None

    # ── Priority 2: free-click on empty map ──────────────────────────────────
    elif lc and lc != st.session_state._last_lc:
        st.session_state._last_lc = lc
        c_lat = round(lc["lat"], 4)
        c_lon = ((round(lc["lng"], 4) + 180) % 360) - 180
        hit = next(((n, c) for n, c in LOCATION_DATABASE.items()
                    if abs(c_lat - c[0]) < 0.03 and abs(c_lon - c[1]) < 0.03), None)
        if hit:
            bname, bcoords = hit
            if (abs(bcoords[0] - st.session_state.lat) > 0.0001 or
                    abs(bcoords[1] - st.session_state.lon) > 0.0001 or
                    st.session_state.is_custom_point):
                st.session_state.lat             = bcoords[0]
                st.session_state.lon             = bcoords[1]
                st.session_state.map_center      = [bcoords[0], bcoords[1]]
                st.session_state.location_name   = bname
                st.session_state.is_custom_point = False
                st.session_state._last_tip       = None
                st.session_state.day_offset      = 0
                st.session_state._skip_prefetch  = True
                st.session_state.sel_date        = date_options[0]
                st.rerun()
        else:
            if abs(c_lat - st.session_state.lat) > 0.0001 or abs(c_lon - st.session_state.lon) > 0.0001:
                st.session_state.lat             = c_lat
                st.session_state.lon             = c_lon
                st.session_state.map_center      = [c_lat, c_lon]
                st.session_state.location_name   = fetch_location_name(c_lat, c_lon)
                st.session_state.is_custom_point = True
                st.session_state._last_tip       = None
                st.session_state.day_offset      = 0
                st.session_state._skip_prefetch  = True
                st.session_state.sel_date        = date_options[0]
                st.rerun()

# ── SKY QUALITY (Transparency/Seeing/Dew Risk) — tính trước khi vào layout ───
def _build_sky_quality(table_data, sun_alts=None):
    """Tính Transparency%, Seeing% và Dew Risk% trung bình cho khung tối thiên văn của đêm.

    - Transparency: dựa trên cloud cover (hệ số cao) + humidity (hệ số nhẹ, ẩm cao/khói
      mù làm mờ ảnh). 100% = trời trong hoàn toàn, khô.
    - Seeing: ước lượng từ wind speed (gió mạnh ở mặt đất → nhiễu động khí quyển cao),
      NHƯNG chỉ có ý nghĩa khi trời quang — nếu mây dày, seeing cũng bị giảm theo
      (không thể "thấy rõ" qua lớp mây). 100% = khí quyển ổn định VÀ trời trong.
    - Dew Risk: humidity càng cao → nguy cơ đọng sương trên ống kính càng cao.
      100% = nguy cơ rất cao (cần dây sưởi kính), 0% = không lo sương.

    Lưu ý: Humidity (độ ẩm tương đối, %) khác Dew Point (điểm sương, °C).
    Ở đây dùng Humidity làm proxy cho Dew Risk vì không có dữ liệu dew point riêng."""
    if not table_data:
        return None
    if len(table_data) > 12:
        table_data = table_data[:-1]
        if sun_alts is not None:
            sun_alts = sun_alts[:-1]
    if sun_alts is None:
        sun_alts = [-90] * len(table_data)

    transp_vals = []
    seeing_vals = []
    dew_vals = []
    for r, sa in zip(table_data, sun_alts):
        if sa is not None and sa > -12:
            continue
        cloud_str = r.get("☁️", "100%")
        humid_str = r.get("💧", "0%")
        wind_str  = r.get("💨", "0m/s")
        cloud_pct = int(cloud_str.replace("%","")) if cloud_str.replace("%","").isdigit() else 100
        humid_pct = int(humid_str.replace("%","")) if humid_str.replace("%","").isdigit() else 0
        try:
            wind_ms = float(wind_str.replace("m/s",""))
        except ValueError:
            wind_ms = 0.0

        # Transparency: trừ điểm theo cloud cover (hệ số cao) và humidity (hệ số nhẹ)
        transp = 100 - cloud_pct * 0.9 - max(0, humid_pct - 60) * 0.5
        transp_vals.append(max(0, min(100, transp)))

        # Seeing: gió nhẹ → ổn định khí quyển tốt. Gió > 2m/s → nhiễu động tăng.
        # Nhân thêm hệ số theo cloud cover — mây dày thì seeing không còn ý nghĩa.
        seeing_atmos = 100 - max(0, wind_ms - 2) * 9
        seeing_atmos = max(0, min(100, seeing_atmos))
        cloud_factor = max(0, 100 - cloud_pct) / 100  # 1.0 nếu trời quang, 0 nếu mây kín
        seeing = seeing_atmos * cloud_factor
        seeing_vals.append(max(0, min(100, seeing)))

        # Dew Risk: humidity ≥ 70% bắt đầu có nguy cơ, ≥ 95% → nguy cơ rất cao
        dew_risk = max(0, (humid_pct - 70)) * (100 / 30)  # 70%→0, 100%→100
        dew_vals.append(max(0, min(100, dew_risk)))

    if not transp_vals:
        return None
    avg_transp = round(sum(transp_vals) / len(transp_vals))
    avg_seeing = round(sum(seeing_vals) / len(seeing_vals))
    avg_dew    = round(sum(dew_vals) / len(dew_vals))
    return {"transparency": avg_transp, "seeing": avg_seeing, "dew_risk": avg_dew}

if st.session_state.day_offset == 0:
    _sky_q = _build_sky_quality(_full_table_data, _full_sun_alt)
else:
    _sky_q = _build_sky_quality(weather_table_data, sun_altitudes)

def _quality_color(val):
    if val >= 75: return "#6ee7b7"   # xanh lá — tốt
    elif val >= 45: return "#fde68a" # vàng — trung bình
    else: return "#fca5a5"           # đỏ — kém

def _quality_label(val):
    if val >= 75: return "Excellent"
    elif val >= 45: return "Average"
    else: return "Poor"

def _risk_color(val):
    """Cho các chỉ số mà cao = xấu (ví dụ Dew Risk)."""
    if val >= 60: return "#fca5a5"   # đỏ — nguy cơ cao
    elif val >= 25: return "#fde68a" # vàng — trung bình
    else: return "#6ee7b7"           # xanh lá — an toàn

def _risk_label(val):
    if val >= 60: return "High"
    elif val >= 25: return "Moderate"
    else: return "Low"

# ── LAYOUT: LEFT PANEL + RIGHT PANEL ─────────────────────────────────────────
st.markdown("""
    <style>
        /* Ép bảng chiếm toàn bộ chiều rộng nhưng cột 2 (Mây) chỉ chiếm 10% */
        [data-testid="stTable"] table { width: 100% !important; table-layout: fixed; }
        [data-testid="stTable"] td:nth-child(2), [data-testid="stTable"] th:nth-child(2) { width: 10% !important; }
        /* Đảm bảo cột 📸 Đánh giá có đủ chỗ hiển thị sao */
        [data-testid="stTable"] td:nth-child(5), [data-testid="stTable"] th:nth-child(5) { width: 35% !important; }
    </style>
""", unsafe_allow_html=True)
col_left, col_right = st.columns([2.5, 1.1])

with col_right:
    # Bortle — model chỉ chính xác trong lãnh thổ Nhật Bản, ẩn nếu ở ngoài
    _in_japan = (24.0 <= st.session_state.lat <= 46.0 and 122.0 <= st.session_state.lon <= 154.0)
    if _in_japan:
        st.markdown(f"""
        <div class="metric-card">
            <span style="color:#94a3b8;font-size:13px;font-weight:bold;">🌌 SKY QUALITY</span>
            <div style="font-size:28px;font-weight:bold;color:#38bdf8;margin-top:5px;">Bortle Class {bortle_class}</div>
            <div style="font-size:14px;color:#e2e8f0;margin-top:2px;">SQM: <b>{sqm_val}</b> mag/arcsec²</div>
        </div>""", unsafe_allow_html=True)

    # Moon Phase + Coordinate — 1 block, trái/phải
    st.markdown(f"""
    <div class="metric-card">
        <div style="display:flex;gap:10px;">
            <div style="flex:1;">
                <span style="color:#94a3b8;font-size:13px;font-weight:bold;">🌙 MOON PHASE</span>
                <div style="font-size:28px;font-weight:bold;color:#fbbf24;margin-top:5px;">{moon_pct}%</div>
                <div style="font-size:12px;color:#cbd5e1;margin-top:4px;font-style:italic;">{moon_text}</div>
            </div>
            <div style="flex:1;border-left:1px solid #334155;padding-left:10px;">
                <span style="color:#94a3b8;font-size:13px;font-weight:bold;">📍 COORDINATE</span>
                <div class="geo-highlight" style="font-size:15px;margin-top:5px;color:#38bdf8;">
                    LON: {round(st.session_state.lon,4)}<br>
                    LAT: {round(st.session_state.lat,4)}
                </div>
            </div>
        </div>
    </div>""", unsafe_allow_html=True)

    # Transparency + Seeing + Dew Risk — 1 block, 3 cột (thay vị trí Position & Coordinate cũ)
    if _sky_q:
        _tc = _quality_color(_sky_q["transparency"])
        _sc = _quality_color(_sky_q["seeing"])
        _dc = _risk_color(_sky_q["dew_risk"])
        _tl = _quality_label(_sky_q["transparency"])
        _sl = _quality_label(_sky_q["seeing"])
        _dl = _risk_label(_sky_q["dew_risk"])
        st.markdown(f"""
        <div class="metric-card">
            <div style="display:flex;gap:8px;">
                <div style="flex:1;text-align:center;">
                    <div style="font-size:10.5px;color:#94a3b8;font-weight:700;letter-spacing:0.04em;">TRANSPARENCY</div>
                    <div style="font-size:22px;font-weight:800;color:{_tc};margin-top:4px;">{_sky_q["transparency"]}%</div>
                    <div style="font-size:11px;color:{_tc};opacity:0.85;margin-top:1px;">{_tl}</div>
                </div>
                <div style="flex:1;text-align:center;border-left:1px solid #334155;">
                    <div style="font-size:10.5px;color:#94a3b8;font-weight:700;letter-spacing:0.04em;">SEEING</div>
                    <div style="font-size:22px;font-weight:800;color:{_sc};margin-top:4px;">{_sky_q["seeing"]}%</div>
                    <div style="font-size:11px;color:{_sc};opacity:0.85;margin-top:1px;">{_sl}</div>
                </div>
                <div style="flex:1;text-align:center;border-left:1px solid #334155;">
                    <div style="font-size:10.5px;color:#94a3b8;font-weight:700;letter-spacing:0.04em;">DEW RISK</div>
                    <div style="font-size:22px;font-weight:800;color:{_dc};margin-top:4px;">{_sky_q["dew_risk"]}%</div>
                    <div style="font-size:11px;color:{_dc};opacity:0.85;margin-top:1px;">{_dl}</div>
                </div>
            </div>
        </div>""", unsafe_allow_html=True)

    # Weather source selectbox + source label
    # Dynamic key theo weather_source → widget re-render đúng khi auto-fallback sang GFS
    source_options = ["JMA", "US (GFS)", "EU (ECMWF)", "🔀 Blend (JMA+ECMWF+GFS)"]
    cur_src = st.session_state.weather_source
    if cur_src not in source_options:
        cur_src = "JMA"
    src_key = f"sel_source_{cur_src.replace(' ', '_').replace('(', '').replace(')', '').replace('🔀','')}"
    chosen = st.selectbox("src", source_options,
                          index=source_options.index(cur_src),
                          label_visibility="collapsed", key=src_key)
    if chosen != st.session_state.weather_source:
        st.session_state.weather_source = chosen
        st.session_state._source_auto = False  # user chọn tay → không auto-switch nữa
        st.rerun()

    # 7-Day Forecast Table — replaces Random Overlap Assumption
    def _cloud_status_icon(cloud_pct, precip=0.0):
        """Return weather icon + label based on cloud cover and precipitation."""
        if precip is not None and precip > 2.0:
            if cloud_pct > 70:
                return "\u26c8\ufe0f", "Storm"
            return "\U0001f327\ufe0f", "Rainy"
        if cloud_pct <= 20:
            return "\u2600\ufe0f", "Sunny"
        elif cloud_pct <= 45:
            return "\u26c5", "Partly"
        elif cloud_pct <= 70:
            return "\U0001f325\ufe0f", "Cloudy"
        else:
            return "\u2601\ufe0f", "Overcast"

    # Build 7-day daily summary from hourly_data
    JST_now = datetime.now(JST)
    _7day_rows = []
    for _doff in range(7):
        _d = (JST_now + timedelta(days=_doff)).replace(tzinfo=None)
        _dpfx = _d.strftime("%Y-%m-%d")
        _day_label = _d.strftime("%a %d/%m")

        _temps, _clouds, _precips = [], [], []
        _tlist = hourly_data.get("time", []) if hourly_data else []
        for _i, _t in enumerate(_tlist):
            if _t.startswith(_dpfx):
                _hr = int(_t[11:13])
                for _sfx in ["_jma_msm", "_gfs_seamless", "_ecmwf_ifs025"]:
                    _v = _get_raw(hourly_data, "temperature_2m", _sfx, _i)
                    if _v is not None:
                        _temps.append((_hr, _v))
                        break
                else:
                    _raw_t = hourly_data.get("temperature_2m", [])
                    if _i < len(_raw_t) and _raw_t[_i] is not None:
                        _temps.append((_hr, float(_raw_t[_i])))
                _cv, _ = get_val(hourly_data, "cloud_cover", _i, prefer_jma)
                _clouds.append(_cv)
                for _sfx in ["_gfs_seamless", "_jma_msm", "_ecmwf_ifs025"]:
                    _pv = _get_raw(hourly_data, "precipitation", _sfx, _i)
                    if _pv is not None:
                        _precips.append(_pv)
                        break

        if _temps:
            _noon = min(_temps, key=lambda x: abs(x[0] - 12))
            _temp_noon = round(_noon[1], 1)
            _temp_min  = round(min(v for _, v in _temps), 1)
            _temp_max  = round(max(v for _, v in _temps), 1)
        else:
            _temp_noon = _temp_min = _temp_max = None

        _avg_cloud = round(sum(_clouds) / len(_clouds)) if _clouds else 0
        _total_precip = round(sum(_precips), 1) if _precips else 0.0
        _icon, _status = _cloud_status_icon(_avg_cloud, _total_precip)

        if _temp_max is not None and _temp_max < 3.0 and _total_precip > 0.5:
            _icon, _status = "\u2744\ufe0f", "Snowy"

        _7day_rows.append({
            "day": _day_label,
            "icon": _icon,
            "status": _status,
            "temp_max": _temp_max,
            "temp_min": _temp_min,
            "cloud": _avg_cloud,
        })

    if _7day_rows:
        _rows7 = ""
        for _r in _7day_rows:
            _tmax_str = f"{_r['temp_max']}\u00b0" if _r['temp_max'] is not None else "\u2014"
            _tmin_str = f"{_r['temp_min']}\u00b0" if _r['temp_min'] is not None else "\u2014"
            _cloud_color = '#22c55e' if _r['cloud'] <= 25 else ('#eab308' if _r['cloud'] <= 50 else ('#f97316' if _r['cloud'] <= 75 else '#ef4444'))
            _rows7 += (
                f'<div style="display:flex;flex-direction:column;align-items:center;gap:3px;'
                f'background:rgba(255,255,255,0.04);border-radius:10px;padding:10px 6px;'
                f'border:1px solid #1e293b;flex:1;min-width:0;">'
                f'<div style="font-size:11px;color:#94a3b8;font-weight:600;white-space:nowrap;'
                f'overflow:hidden;text-overflow:ellipsis;max-width:100%;text-align:center;">{_r["day"]}</div>'
                f'<div style="font-size:26px;line-height:1.1;">{_r["icon"]}</div>'
                f'<div style="font-size:11px;color:#cbd5e1;font-weight:500;">{_r["status"]}</div>'
                f'<div style="font-size:13px;font-weight:700;color:#f97316;">{_tmax_str}</div>'
                f'<div style="font-size:11px;color:#60a5fa;">{_tmin_str}</div>'
                f'<div style="font-size:10px;color:{_cloud_color};margin-top:2px;">{_r["cloud"]}%</div>'
                f'</div>'
            )
        _forecast_html = (
            '<div style="margin-top:8px;">'
            '<div style="font-size:12px;color:#94a3b8;font-weight:700;margin-bottom:6px;letter-spacing:0.5px;">'
            '\U0001f5d3\ufe0f 7-DAY FORECAST</div>'
            '<div style="display:flex;gap:4px;width:100%;">'
            + _rows7 +
            '</div>'
            '<div style="font-size:10px;color:#475569;margin-top:5px;text-align:right;">'
            '\u2191 High &nbsp;\u2193 Low &nbsp;\u2601 Cloud%</div>'
            '</div>'
        )
        st.markdown(_forecast_html, unsafe_allow_html=True)


with col_left:
    # Inject CSS:
    # 1. Orange styling for date selectbox (nav2)
    # 2. Compact styling for location selectbox (nav3) — smaller font, tighter padding
    st.markdown("""
<style>
/* ── Pull col_left content closer to map ── */
.st-key-nav_box { margin-top: -58px !important; }

/* ── Date selectbox: shrink to fit content ── */
[data-testid="stSelectbox"]:has(select[id*="sel_date"]) {
    width: fit-content !important;
    min-width: 0 !important;
}
[data-testid="stSelectbox"]:has(select[id*="sel_date"]) div[data-baseweb="select"] {
    width: fit-content !important;
    min-width: 0 !important;
}
[data-testid="stSelectbox"]:has(select[id*="sel_date"]) div[data-baseweb="select"] > div:first-child {
    background: rgba(154,52,18,0.60) !important;
    border: 1.5px solid rgba(234,88,12,0.75) !important;
    box-shadow: 0 0 8px rgba(234,88,12,0.18) !important;
    padding-left: 6px !important;
    padding-right: 6px !important;
}
[data-testid="stSelectbox"]:has(select[id*="sel_date"]) span {
    color: #fb923c !important;
    font-weight: 700 !important;
    font-size: 12px !important;
}

/* LPM button is now a floating map control (bottomright) */

/* ── NAV BOX: khung ngoài chứa 2 hàng con ──────────────────────────────────
   nav_row1: ⬅️  date  ➡️   → luôn nằm 1 hàng (no-wrap)
   nav_row2: location  LPM  → luôn nằm 1 hàng (no-wrap)
   - PC (rộng ≥ 600px): nav_row1 và nav_row2 nằm cùng 1 hàng ngang
   - iPhone (< 600px):  nav_row1 hàng trên, nav_row2 hàng dưới
   Cấu trúc DOM: .st-key-nav_box → stVerticalBlock → stElementContainer ×2
                 (mỗi cái wrap 1 sub-container nav_row1 / nav_row2)       */

/* --- nav_box: outer flex row, wrap trên mobile --- */
.st-key-nav_box,
.st-key-nav_box > div,
.st-key-nav_box [data-testid="stVerticalBlockBorderWrapper"],
.st-key-nav_box [data-testid="stVerticalBlockBorderWrapper"] > div {
    width: 100% !important;
}
.st-key-nav_box > div > [data-testid="stVerticalBlock"] {
    display: flex !important;
    flex-direction: row !important;
    flex-wrap: wrap !important;
    align-items: center !important;
    gap: 6px !important;
    width: 100% !important;
    background: rgba(255,255,255,0.03);
    border: 1px solid #1e293b;
    border-radius: 10px;
    padding: 6px;
    box-sizing: border-box;
}
/* Mỗi stElementContainer con trực tiếp của nav_box → chiếm auto */
.st-key-nav_box > div > [data-testid="stVerticalBlock"] > [data-testid="stElementContainer"] {
    margin: 0 !important;
    flex: 0 0 auto;
}

/* --- nav_row1: ⬅️ date ➡️ — không bao giờ wrap, co lại theo nội dung --- */
.st-key-nav1,
.st-key-nav1 > div,
.st-key-nav1 [data-testid="stVerticalBlockBorderWrapper"],
.st-key-nav1 [data-testid="stVerticalBlockBorderWrapper"] > div { width: auto !important; }
.st-key-nav1 [data-testid="stVerticalBlock"] {
    display: flex !important;
    flex-direction: row !important;
    flex-wrap: nowrap !important;
    align-items: center !important;
    gap: 6px !important;
    width: auto !important;
}
.st-key-nav1 [data-testid="stElementContainer"] { margin: 0 !important; flex: 0 0 auto; }
.st-key-nav1 [data-testid="stButton"] button {
    width: 44px !important; min-width: 0 !important; padding: 0 !important;
}
.st-key-nav1 [data-testid="stElementContainer"]:has([data-testid="stButton"]) { flex: 0 0 44px; }
.st-key-nav1 [data-testid="stElementContainer"]:has(select[id*="sel_date"]) { flex: 0 1 auto; }
.st-key-nav1 [data-testid="stElementContainer"]:has(select[id*="sel_date"]) [data-testid="stSelectbox"] {
    width: fit-content !important;
}

/* nav2 (location+LPM) removed — now shown as floating label on map */

</style>""", unsafe_allow_html=True)

    # Nav controls — chỉ còn nav1: ⬅️  date  ➡️
    nav_box = st.container(key="nav_box")
    with nav_box:
        with st.container(key="nav1"):
            def _go_prev():
                if st.session_state.day_offset > 0:
                    st.session_state.day_offset -= 1
                    st.session_state.sel_date = date_options[st.session_state.day_offset]

            def _go_next():
                if st.session_state.day_offset < 6:
                    st.session_state.day_offset += 1
                    st.session_state.sel_date = date_options[st.session_state.day_offset]

            st.button("⬅️", key="btn_prev", on_click=_go_prev)

            sel_label = st.selectbox("ngay", date_options, index=st.session_state.day_offset,
                                     label_visibility="collapsed",
                                     key="sel_date")
            new_off = date_options.index(sel_label)
            if new_off != st.session_state.day_offset:
                st.session_state.day_offset = new_off
                st.rerun()

            st.button("➡️", key="btn_next", on_click=_go_next)





    # Table — custom styled HTML card
    if weather_table_data:
        # Hiện badge nếu đang dùng fallback endpoint
        if _ep_label == "no_jma":
            st.markdown('<div style="background:#422006;border:1px solid #f97316;border-radius:8px;'
                        'padding:6px 14px;margin-bottom:8px;font-size:13px;color:#fed7aa;">'
                        '⚠️ JMA MSM サーバーエラー — 代わりに <b>ECMWF + GFS</b> を使用しています</div>',
                        unsafe_allow_html=True)
        elif _ep_label == "gfs_only":
            st.markdown('<div style="background:#422006;border:1px solid #f97316;border-radius:8px;'
                        'padding:6px 14px;margin-bottom:8px;font-size:13px;color:#fed7aa;">'
                        '⚠️ JMA/ECMWF サーバーエラー — 代わりに <b>GFS のみ</b> を使用しています</div>',
                        unsafe_allow_html=True)
        def _cloud_icon_cell(pct_str, precip_val=0.0, temp_val=None):
            pct = int(pct_str.replace('%',''))
            if precip_val is not None and precip_val > 0.5:
                if temp_val is not None and temp_val < 1.0:
                    icon, col = '\u2744\ufe0f', '#93c5fd'
                elif pct > 70:
                    icon, col = '\u26c8\ufe0f', '#f87171'
                else:
                    icon, col = '\U0001f327\ufe0f', '#60a5fa'
            elif pct <= 20:
                icon, col = '\u2600\ufe0f', '#fbbf24'
            elif pct <= 45:
                icon, col = '\u26c5', '#fcd34d'
            elif pct <= 70:
                icon, col = '\U0001f325\ufe0f', '#94a3b8'
            else:
                icon, col = '\u2601\ufe0f', '#64748b'
            return (f'<div style="display:flex;align-items:center;gap:2px;white-space:nowrap;">'
                    f'<span style="font-size:15px;line-height:1;">{icon}</span>'
                    f'<span style="font-size:11px;color:{col};font-weight:600;">{pct_str}</span>'
                    f'</div>')

        def _wind_icon(ws_str):
            ws = float(ws_str.replace('m/s',''))
            if ws < 2:   icon,col = '','#94a3b8'
            elif ws < 5: icon,col = '','#60a5fa'
            else:        icon,col = '','#f97316'
            return f'<span style="color:{col}">{icon} {ws_str}</span>'

        rows_html = ''
        for i, row in enumerate(weather_table_data):
            bg = 'rgba(234,88,12,0.10)' if i % 2 == 0 else 'rgba(194,65,12,0.06)'
            time_lbl = row['⏰']
            cloud_cell = _cloud_icon_cell(row['☁️'], row.get('_precip', 0.0), row.get('_temp'))
            humid_val  = row['💧']
            wind_cell  = _wind_icon(row['💨'])
            stars      = row['📸']
            rows_html += (
                f'<tr style="background:{bg};border-bottom:1px solid rgba(234,88,12,0.18);">'
                f'<td style="padding:8px 8px;font-weight:700;color:#fb923c;white-space:nowrap;">{time_lbl}</td>'
                f'<td style="padding:8px 8px;overflow:hidden;">{cloud_cell}</td>'
                f'<td style="padding:8px 8px;color:#fb923c;">{humid_val}</td>'
                f'<td style="padding:8px 8px;color:#fb923c;">{wind_cell}</td>'
                f'<td style="padding:8px 8px;font-size:16px;letter-spacing:1px;">{stars}</td>'
                f'</tr>'
            )

        table_html = f"""
<div style="background:#1a0a00;border:1.5px solid rgba(234,88,12,0.45);border-radius:12px;overflow:hidden;margin-bottom:8px;box-shadow:0 0 20px rgba(234,88,12,0.10);">
  <table style="width:100%;border-collapse:collapse;font-size:14px;font-family:'Segoe UI',sans-serif;table-layout:fixed;">
    <thead>
      <tr style="background:linear-gradient(90deg,rgba(154,52,18,0.90),rgba(120,40,10,0.75));border-bottom:2px solid rgba(234,88,12,0.55);">
        <th style="padding:10px 8px;text-align:left;color:#fb923c;font-weight:700;width:14%;">⏰</th>
        <th style="padding:10px 8px;text-align:left;color:#fb923c;font-weight:700;width:20%;">🌤️</th>
        <th style="padding:10px 8px;text-align:left;color:#fb923c;font-weight:700;width:13%;">💧</th>
        <th style="padding:10px 8px;text-align:left;color:#fb923c;font-weight:700;width:16%;">💨</th>
        <th style="padding:10px 8px;text-align:left;color:#fb923c;font-weight:700;width:37%;">📸</th>
      </tr>
    </thead>
    <tbody>{rows_html}</tbody>
  </table>
</div>"""
        st.markdown(table_html, unsafe_allow_html=True)
    else:
        # Hiển thị nguyên nhân thực tế thay vì hardcode "502 Bad Gateway"
        if _last_error == "timeout":
            _err_title = "⚠️ Open-Meteo API がタイムアウトしました"
            _err_detail = (
                'リクエストが <b>25秒</b> 以内に応答しませんでした。'
                'サーバーが混雑している可能性があります。<br><br>'
                '<span style="color:#94a3b8;">通常は数分で回復します。'
                '<b>再試行</b> ボタンでキャッシュを削除して再取得してください。</span>'
            )
        elif _last_error and _last_error.startswith("HTTP 5"):
            _code = _last_error.split(" ")[1]
            _err_title = f"⚠️ Open-Meteo API が一時的に応答していません"
            _err_detail = (
                f'サーバー <code style="color:#fbbf24;">api.open-meteo.com</code> が '
                f'<b>{_code} エラー</b> を返しました — これは提供元側の問題で、'
                'アプリ側のエラーではありません。<br><br>'
                '<span style="color:#94a3b8;">通常5～30分で自動的に回復します。'
                '<b>再試行</b> ボタンでキャッシュを削除して再取得してください。</span>'
            )
        elif _last_error and _last_error.startswith("connection_error"):
            _err_title = "⚠️ Open-Meteo API に接続できません"
            _err_detail = (
                'ネットワーク接続エラーが発生しました。'
                'インターネット接続を確認してください。<br><br>'
                '<span style="color:#94a3b8;"><b>再試行</b> ボタンでキャッシュを削除して再取得してください。</span>'
            )
        else:
            _err_title = "⚠️ Open-Meteo API が一時的に応答していません"
            _err_detail = (
                f'予期しないエラーが発生しました'
                + (f'（詳細: <code style="color:#fbbf24;">{_last_error}</code>）' if _last_error else '')
                + '。<br><br>'
                '<span style="color:#94a3b8;">通常は数分で回復します。'
                '<b>再試行</b> ボタンでキャッシュを削除して再取得してください。</span>'
            )
        st.markdown(f"""
<div style="background:#1e293b;border:1px solid #ef4444;border-radius:12px;padding:20px 24px;margin-top:8px;">
    <div style="font-size:18px;font-weight:700;color:#ef4444;margin-bottom:8px;">
        {_err_title}
    </div>
    <div style="color:#cbd5e1;font-size:14px;line-height:1.7;">
        {_err_detail}
    </div>
</div>""", unsafe_allow_html=True)
        if st.button("🔄 再試行", key="btn_retry_weather"):
            st.cache_data.clear()
            st.rerun(scope="app")

# ── MOON + SUN + MILKY WAY ALTITUDE CHART ────────────────────────────────────
st.markdown("---")
st.markdown("### 📊 MOON, SUN & MILKY WAY ALTITUDE(°)")

import plotly.graph_objects as go

# ── Sun brightness: opacity gradient theo Sun altitude ────────────────────────
# Sun > 0°  → cam đậm | Sun 0°~-13° → mờ dần | Sun <= -13° → tắt hẳn (full dark)
def _sun_bright_opacity(sun_alt):
    if sun_alt <= -13:
        return 0.0
    op = (sun_alt + 13) / 23.0 * 0.50   # -13°→0.0, 0°→0.28, +10°→0.50
    return round(min(max(op, 0.0), 0.50), 3)

fig = go.Figure()

# ── Background brightness bands (vrect per slot) ─────────────────────────────
_x_positions = list(range(len(hours_labels)))
for _i, (_lbl, _sa) in enumerate(zip(hours_labels, sun_altitudes)):
    _op = _sun_bright_opacity(_sa)
    if _op > 0.005:
        fig.add_vrect(
            x0=_i - 0.5, x1=_i + 0.5,
            fillcolor="rgba(251,146,60,1.0)",
            opacity=_op,
            layer="below",
            line_width=0,
        )

# ── Moon: filled area ─────────────────────────────────────────────────────────
fig.add_trace(go.Scatter(
    x=_x_positions, y=moon_altitudes,
    mode='lines',
    name='🌙 Moon',
    line=dict(color='#fbbf24', width=2.5),
    fill='tozeroy',
    fillcolor='rgba(251,191,36,0.20)',
    hovertemplate='%{customdata}<br>Moon: %{y:.1f}°<extra></extra>',
    customdata=hours_labels,
))

# ── Sun: dashed blue line ─────────────────────────────────────────────────────
fig.add_trace(go.Scatter(
    x=_x_positions, y=sun_altitudes,
    mode='lines',
    name='☀️ Sun',
    line=dict(color='#38bdf8', width=2.5, dash='dash'),
    hovertemplate='%{customdata}<br>Sun: %{y:.1f}°<extra></extra>',
    customdata=hours_labels,
))

# ── Milky Way GC: dashed purple ───────────────────────────────────────────────
fig.add_trace(go.Scatter(
    x=_x_positions, y=milkyway_altitudes,
    mode='lines',
    name='🌌 MW GC',
    line=dict(color='#a78bfa', width=2.0, dash='dot'),
    hovertemplate='%{customdata}<br>MW GC: %{y:.1f}°<extra></extra>',
    customdata=hours_labels,
))

# ── Horizon rule ──────────────────────────────────────────────────────────────
fig.add_hline(y=0, line=dict(color='#475569', dash='dot', width=1))

# ── -13° rule ─────────────────────────────────────────────────────────────────
fig.add_hline(y=-13, line=dict(color='rgba(251,146,60,0.50)', dash='dot', width=1),
              annotation_text="−13° full dark", annotation_font_color="rgba(251,146,60,0.7)",
              annotation_position="bottom right")

# ── Layout ────────────────────────────────────────────────────────────────────
fig.update_layout(
    height=480,
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(15,23,42,0.0)',
    font=dict(color='#94a3b8', size=12),
    xaxis=dict(
        tickmode='array',
        tickvals=_x_positions,
        ticktext=hours_labels,
        gridcolor='rgba(71,85,105,0.3)',
        title='Time 18:00 ~ 06:00',
        title_font_color='#94a3b8',
    ),
    yaxis=dict(
        gridcolor='rgba(71,85,105,0.3)',
        title=None,
        zeroline=False,
    ),
    legend=dict(
        orientation='h', yanchor='bottom', y=1.02, xanchor='left', x=0,
        font=dict(color='#cbd5e1'),
        bgcolor='rgba(0,0,0,0)',
    ),
    margin=dict(l=50, r=20, t=40, b=40),
    hovermode='x unified',
)

st.plotly_chart(fig, use_container_width=True)

# Legend note
st.markdown(
    "<div style='text-align:center;font-size:12px;color:#94a3b8;margin-top:-8px;'>"
    "<span style='color:#fbbf24;'>▬</span> Moon &nbsp;&nbsp;"
    "<span style='color:#38bdf8;'>╌╌</span> Sun &nbsp;&nbsp;"
    "<span style='color:#a78bfa;'>·····</span> Milky Way &nbsp;&nbsp;|&nbsp;&nbsp;"
    "<span style='color:rgba(251,146,60,0.8);'>▓▒░</span> Sky brightness gradient (trully dark when Sun &lt;−13°)</div>",
    unsafe_allow_html=True
)




# ── FOOTER ────────────────────────────────────────────────────────────────────
st.markdown('<div class="footer-copyright">© Copyright: insta: fcbmkw</div>', unsafe_allow_html=True)
