import asyncio
import aiohttp
import json

# MIT License: https://github.com/Ryuguu-Chan/Japan-romanization
kana_dict = {
    # ==========================| Hiragana | ==========================
    "あ" : "a",  "い" : "i",  "う" : "u",  "え" : "e",  "お" : "o",
    "か" : "ka", "き" : "ki", "く" : "ku", "け" : "ke", "こ" : "ko",
    "が" : "ga", "ぎ" : "gi", "ぐ" : "gu", "げ" : "ge", "ご" : "go",
    "さ" : "sa", "し" : "shi", "す" : "su", "せ" : "se", "そ" : "so",
    "ざ" : "za", "じ" : "ji", "ず" : "zu", "ぜ" : "ze", "ぞ" : "zo",
    "た" : "ta", "ち" : "chi", "つ" : "tsu", "て" : "te", "と" : "to", 
    "だ" : "da", "ぢ" : "ji", "づ" : "zu", "で" : "de", "ど" : "do", 
    "な" : "na", "に" : "ni", "ぬ" : "nu", "ね" : "ne", "の" : "no",
    "は" : "ha", "ひ" : "hi", "ふ" : "fu", "へ" : "he", "ほ" : "ho",
    "ば" : "ba", "び" : "bi", "ぶ" : "bu", "べ" : "be", "ぼ" : "bo", 
    "ぱ" : "pa", "ぴ" : "pi", "ぷ" : "pu", "ぺ" : "pe", "ぽ" : "po", 
    "ま" : "ma", "み" : "mi", "む" : "mu", "め" : "me", "も" : "mo", 
    "や" : "ya",             "ゆ" : "yu", "𛀁" : "ye", "よ" : "yo", 
    "ら" : "ra", "り" : "ri", "る" : "ru", "れ" : "re", "ろ" : "ro", 
    "わ" : "wa", "ゐ" : "wi",              "ゑ" : "we", "を" : "wo",
    "ん" : "n", "て" : "te",
    # ===========================| katakana |==========================
    "ア" : "a",  "イ" : "i",  "ウ" : "u",  "エ" : "e",  "オ" : "o",
    "カ" : "ka", "キ" : "ki", "ク" : "ku", "ケ" : "ke", "コ" : "ko",
    "ガ" : "ga", "ギ" : "gi", "グ" : "gu", "ゲ" : "ge", "ゴ" : "go",
    "サ" : "sa", "シ" : "shi", "ス" : "su", "セ" : "se", "ソ" : "so",
    "ザ" : "za", "ジ" : "ji", "ズ" : "zu", "ゼ" : "ze", "ゾ" : "zo",
    "タ" : "ta", "チ" : "chi", "ツ" : "tsu", "テ" : "te", "ト" : "to", 
    "ダ" : "da", "ヂ" : "ji", "ヅ" : "zu", "デ" : "de", "ド" : "do", 
    "ナ" : "na", "ニ" : "ni", "ヌ" : "nu", "ネ" : "ne", "ノ" : "no",
    "ハ" : "ha", "ヒ" : "hi", "フ" : "fu", "ヘ" : "he", "ホ" : "ho", 
    "バ" : "ba", "ビ" : "bi", "ブ" : "bu", "ベ" : "be", "ボ" : "bo", 
    "パ" : "pa", "ピ" : "pi", "プ" : "pu", "ペ" : "pe", "ポ" : "po", 
    "マ" : "ma", "ミ" : "mi", "ム" : "mu", "メ" : "me", "モ" : "mo", 
    "ヤ" : "ya ",             "ユ" : "yu", "𛀀" : "ye", "ヨ" : "yo", 
    "ラ" : "ra", "リ" : "ri", "ル" : "ru", "レ" : "re", "ロ" : "ro", 
    "ワ" : "wa", "ヰ" : "wi",              "ヱ" : "we", "ヲ" : "wo",
    "ン" : "n", "テ" : "te", "・" : " ", " " : " "
}

digraph_dict = {
    # ===========================| katakana |==========================
    "キャ" : "ε", "キュ" : "ю", "キョ" : "έ", "キィ" : "ж", "キァ" : "═",
    "シャ" : "β", "シュ" : "χ", "ショ" : "ὲ", "シィ" : "џ", "シァ" : "║",
    "チャ" : "α", "チュ" : "ψ", "チョ" : "ά", "チィ" : "њ", "チァ" : "╒",
    "ニャ" : "γ", "ニュ" : "ω", "ニョ" : "ὰ", "ニィ" : "љ", "ニァ" : "╓",
    "ヒャ" : "д", "ヒュ" : "ρ", "ヒョ" : "ώ", "ヒィ" : "є", "ヒァ" : "╔",
    "ミャ" : "ζ", "ミュ" : "ς", "ミョ" : "ύ", "ミィ" : "ѓ", "ミァ" : "╕",
    "リャ" : "η", "リュ" : "π", "リョ" : "ό", "リィ" : "ђ", "リァ" : "╖",
    "ギャ" : "μ", "ギュ" : "Σ", "ギョ" : "ϋ", "ギィ" : "э", "ギァ" : "╗",
    "ジャ" : "ι", "ジュ" : "Φ", "ジョ" : "ϊ", "ジィ" : "҂", "ジァ" : "╘",
    "ヂャ" : "ι", "ヂュ" : "Φ", "ヂョ" : "ϊ", "ヂィ" : "Ҥ", "ヂァ" : "╙",
    "ビャ" : "κ", "ビュ" : "Ξ", "ビョ" : "Δ", "ビィ" : "п", "ビァ" : "╚",
    "ピャ" : "ш", "ピュ" : "Λ", "ピョ" : "Θ", "ピィ" : "Ӹ", "ピァ" : "╛",
    "テャ" : "∌", "テュ" :"∬", "テョ" : "∦", "ティ" : "⊕", "テァ" : "╜",
    "フャ" : "Æ", "フュ" :"Þ", "フョ" : "§", "フィ" : "¬", "ファ" : "¶",
    # ==========================| Hiragana | ==========================
    "きゃ" : "ε", "きゅ" : "ю", "きょ" : "έ", "きぃ" : "ж", "きぁ" : "═",
    "しゃ" : "β", "しゅ" : "χ", "しょ" : "ὲ", "しぃ" : "џ", "しぁ" : "║",
    "ちゃ" : "α", "ちゅ" : "ψ", "ちょ" : "ά", "ちぃ" : "њ", "ちぁ" : "╒",
    "にゃ" : "γ", "にゅ" : "ω", "にょ" : "ὰ", "にぃ" : "љ", "にぁ" : "╓",
    "ひゃ" : "д", "ひゅ" : "ρ", "ひょ" : "ώ", "ひぃ" : "є", "ひぁ" : "╔",
    "みゃ" : "ζ", "みゅ" : "ς", "みょ" : "ύ", "みぃ" : "ѓ", "みぁ" : "╕",
    "りゃ" : "η", "りゅ" : "π", "りょ" : "ό", "りぃ" : "ђ", "りぁ" : "╖",
    "ぎゃ" : "μ", "ぎゅ" : "Σ", "ぎょ" : "ϋ", "ぎぃ" : "э", "ぎぁ" : "╗",
    "じゃ" : "ι", "じゅ" : "Φ", "じょ" : "ϊ", "じぃ" : "҂", "じぁ" : "╘",
    "ぢゃ" : "ι", "ぢゅ" : "Φ", "ぢょ" : "ϊ", "ぢぃ" : "҂", "ぢぁ" : "╘",
    "びゃ" : "κ", "びゅ" : "Ξ", "びょ" : "Δ", "びぃ" : "п", "びぁ" : "╚",
    "ぴゃ" : "ш", "ぴゅ" : "Λ", "ぴょ" : "Θ", "ぴぃ" : "Ӹ", "ぴぁ" : "╛",
    "てゃ" : "∌", "てゅ" : "∬", "てょ" : "∦", "てぃ" : "⊕", "てぁ" : "╜",
    "ふゃ" : "Æ", "ふゅ" : "Þ", "ふょ" : "§", "ふぃ" : "¬", "ふぁ" : "¶"
}

digraph_ref = {
    "ε" : "kya", "ю" : "kyu", "έ" : "kyo", "ж" : "ki" , "═" : "kia",
    "β" : "sha", "χ" : "shu", "ὲ" : "sho", "џ" : "shi", "║" : "shia",
    "α" : "cha", "ψ" : "chi", "ά" : "cho", "њ" : "chi", "╒" : "chia",
    "γ" : "nya", "ω" : "nyu", "ὰ" : "nyo", "љ" : "ni" , "╓" : "nia",
    "д" : "hya", "ρ" : "hyu", "ώ" : "hyo", "є" : "hi" , "╔" : "hia",
    "ζ" : "mya", "ς" : "myu", "ύ" : "myo", "ѓ" : "mi" , "╕" : "mia",
    "η" : "rya", "π" : "ryu", "ό" : "ryo", "ђ" : "ri" , "╖" : "ria",
    "μ" : "gya", "Σ" : "gyu", "ϋ" : "gyo", "э" : "gi" , "╗" : "gia",
    "ι" : "ja" , "Φ" : "ju" , "ϊ" : "jo" , "҂" : "ji" , "╘" : "jia",
    "κ" : "bya", "Ξ" : "byu", "Δ" : "byo", "п" : "bi" , "╚" : "bia",
    "ш" : "pya", "Λ" : "pyu", "Θ" : "pyo", "Ӹ" : "pi" , "╛" : "pia",
    "∌" : "tya", "∬" : "tyu", "∦" : "tyo", "⊕" : "ti", "╜" : "tea",
    "Æ" : "fa", "Þ" : "fu", "§" : "fo", "¬" : "fi", "¶" : "fa"
}

digraph_arr = [
    "ャ", "ュ", "ョ", "ィ", "ァ",
    "ゃ", "ゅ", "ょ", "ぃ", "ぁ",
]

async def fetchJisho(text):
    try:
        jishoJson = await makeJsonRequest(f"http://jisho.org/api/v1/search/words?keyword={text}")
        if len(jishoJson.get("data", [])) > 0:
            return jishoJson
        else:
            return False
    except:
        return None

async def makeJsonRequest(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            reqdata = await resp.json()
            return reqdata

def make_results(jishoJson):
    results = []
    for jishoResult in jishoJson.get("data", []):
        results.append(make_result_single(jishoResult))
    return results

def make_result_single(jishoResult):
    # Meta
    jisho_src = None
    if jishoResult.get("slug"):
        jisho_src = f"https://jisho.org/word/{jishoResult.get('slug')}"
    kanji = jishoResult["japanese"][0].get("word", None)
    kana = jishoResult["japanese"][0].get("reading", None)
    word = kanji or kana
    reading = None
    if kanji and kana:
        reading = kana+" "+to_romaji(str(kana))
    elif kana:
        reading = to_romaji(str(kana))
    is_common = None
    if jishoResult.get("is_common", None) is True:
        is_common = "Common"
    jlpt = None
    if len(jishoResult.get("jlpt", [])) > 0:
        jlpt = str(", ".join(jishoResult.get("jlpt", [])))
    tags = None
    if len(jishoResult.get("tags", [])) > 0:
        tags = str(", ".join(jishoResult.get("tags", [])))
    attribution = None
    if jishoResult.get("attribution", None) is not None:
        attrs = ["Jisho API"]
        for k, v in jishoResult.get("attribution", {}).items():
            if v is not False:
                attrs.append(k)
        attribution = "Results from "+", ".join(attrs)

    # Senses
    senses = []
    for index, sense in enumerate(jishoResult.get("senses", [])):
        parts_of_speech = None
        if len(sense.get("parts_of_speech")) > 0:
            parts_of_speech = str(", ".join(sense.get("parts_of_speech", [])))
            parts_of_speech = "*"+parts_of_speech+"*"
        english_definitions = None
        if sense.get("english_definitions"):
            english_definitions = str("; ".join(sense.get("english_definitions", [])))
        sense_tags = None
        if len(sense.get("tags", [])) > 0:
            sense_tags = "*Tags: " + str(", ".join(sense.get("tags", []))) + "*"
        see_also = None
        if len(sense.get("see_also", [])) > 0:
            see_also = "*See also: " + str(", ".join(sense.get("see_also", []))) + "*"
        links = None
        if len(sense.get("links", [])) > 0:
            links = ""
            for sl in sense.get("links", []):
                if sl.get("url") is not None:
                    links += f"[{sl.get('text', 'Link')}]({sl.get('url')}), "
            links = links[:-2] # remove last comma and space
        senses.append({
            "name": str(index+1)+". "+english_definitions,
            "value": ("\n".join(filter(None, [parts_of_speech, sense_tags, see_also, links])) or "-"),
        })

    return {
      "title": str(word),
      "url": jisho_src,
      "description": " ・ ".join(filter(None, [reading, is_common, jlpt, tags])),
      "senses": senses,
      "attribution": attribution
    }

def to_romaji(text: str):
    final_str = ""
    text_arr = list(text)
    text_arr_len = len(text_arr)-1
    pointer = 0

    for idx, letter in enumerate(text_arr):
        try:
            # Check for digraph
            if idx < pointer:
                continue
            elif idx < text_arr_len and text_arr[idx+1] in digraph_arr:
                # Skip pointer past the digraph
                final_str += str(digraph_ref[str(digraph_dict[str(text_arr[idx])+str(text_arr[idx+1])])])
                pointer += 1
            elif letter == "ー":
                # Repeat the last letter
                final_str += final_str[-1]
            elif (letter == "っ" or letter == "ッ"):
                # Repeat the next letter
                if idx < text_arr_len:
                    final_str += str(kana_dict[str(text_arr[idx+1])])[0]
                else:
                    final_str += "."
            else:
                final_str += str(kana_dict[str(text_arr[idx])])
        except:
            # Skip over invalid character
            continue
        pointer += 1
    return final_str
