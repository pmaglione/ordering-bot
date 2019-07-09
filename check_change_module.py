import sys
import spacy
from collections import Counter
import en_core_web_lg
nlp = en_core_web_lg.load()
from spacy.lang.en import LEMMA_INDEX, LEMMA_EXC, LEMMA_RULES
from spacy.lemmatizer import Lemmatizer
lemmatizer = Lemmatizer(LEMMA_INDEX, LEMMA_EXC, LEMMA_RULES)

class Sentence:
    """This class represents a sentences and computes the main components: noun, adjective and number"""
    def __init__(self, sentence):
        self.doc = nlp(sentence) #tokenize the sentence
        self.sentence = sentence
        self.nouns = self.get_nouns()
        self.noun = self.get_main_noun() 
        self.adjetive = self.get_adjetive()
        self.adposition = self.get_adposition()
        self.number = self.get_number()
        
    def __str__(self):
        return self.noun

    def get_similarity(self, words):
        """Return a float percentage of the similarity using Word Vectors"""
        return max([nlp(self.noun).similarity(nlp(word)) for word in words])
    
    def get_noun_chunks(self):
        """Return the nouns chunks objects"""
        return self.doc.noun_chunks
    
    def get_nouns(self):
        """Return the nouns as string"""
        nouns = []
        for chunk in self.get_noun_chunks():
            nouns.append(chunk.root.text)
            
        return nouns
    
    def get_main_noun(self):
        """Return the sentence main noun"""
        return self.nouns[-1]
    
    def get_nouns_amount(self):
        """Return the amount of nouns"""
        return len(list(self.doc.noun_chunks))
    
    def get_referenced_pwrds(self, ptags):
        """Return the words by type and word context"""
        sentences = [sent for sent in self.doc.sents if self.noun in sent.string]     
        pwrds = []
        for sent in sentences:
            for word in sent:
                for _ in word.string: 
                       pwrds.extend([child.string.strip() for child in word.children if child.pos_ in ptags])
        
        return pwrds
        
    def get_adjetive(self):
        """Return the adjetives and nouns referencing to the sentence main noun"""
        ptags = ['ADJ', 'NOUN']
        pwrds = self.get_referenced_pwrds(ptags)
        return ' '.join([x[0] for x in Counter(pwrds).most_common(10) if x[0] not in self.nouns])
    
    def get_adposition(self):
        """Returns the adpositions referencing to the sentence main noun"""
        ptags = ['ADP']
        pwrds = self.get_referenced_pwrds(ptags)
        return ' '.join([x[0] for x in Counter(pwrds).most_common(1)])
    
    def get_number(self):
        """Returns the int number of the sentence independently being a word or int"""
        nums = [self.text2int(token.lemma_) for token in self.doc if token.pos_ == "NUM"]
        if nums:
            return nums[0]
        else:
            return 0 if self.is_plural(self.noun) else 1
        
    def is_total_replace(self):
        """Return boolean if the nouns are plural and no number is detected"""
        return all([self.is_plural(w) for w in self.nouns]) and self.number == 0
        
    def is_plural(self, word):
        """Return if a word is in the plural form"""
        lemma = lemmatizer(word, u'NOUN')
        return True if word is not lemma[0] else False
 
    def text2int(self, textnum):
        """Converts a text num to int"""
        if str(textnum).isdigit():
            return int(textnum)
        else:
            numwords = {}
            units = [
            "zero", "one", "two", "three", "four", "five", "six", "seven", "eight",
            "nine", "ten", "eleven", "twelve", "thirteen", "fourteen", "fifteen",
            "sixteen", "seventeen", "eighteen", "nineteen",
            ]

            tens = ["", "", "twenty", "thirty", "forty", "fifty", "sixty", "seventy", "eighty", "ninety"]

            scales = ["hundred", "thousand", "million", "billion", "trillion"]

            numwords["and"] = (1, 0)
            for idx, word in enumerate(units):    numwords[word] = (1, idx)
            for idx, word in enumerate(tens):     numwords[word] = (1, idx * 10)
            for idx, word in enumerate(scales):   numwords[word] = (10 ** (idx * 3 or 2), 0)

            current = result = 0
            for word in textnum.split():
                if word not in numwords:
                    raise Exception("Illegal word: " + word)

                scale, increment = numwords[word]
                current = current * scale + increment
                if scale > 100:
                    result += current
                    current = 0

            num = result + current
            return num


class OrderManager():
    """This class manages the orders, computes the sentences and generates the new order"""
    def __init__(self, check, new_order):
        self.check = check
        self.new_order = new_order
        self.new_check = []
        self.check_sts = {}
        self.init_sentences()
        self.new_check = self.make_change()
    
    def init_sentences(self):
        """Convert items in Sentence objects and calculates the similarity"""
        self.new_order_st = Sentence(self.new_order)
    
        for key, item in enumerate(self.check):
            item_st = Sentence(item)
            self.check_sts[key] = {
                                'obj': item_st,
                                'similarity': item_st.get_similarity(self.new_order_st.nouns)
                             }
            
    def get_more_similar_item_id(self):
        """Get the item to be replaced comparing the similarity"""
        item_more_similar = max(self.check_sts.items(), key=lambda k: k[1]['similarity'])
        return item_more_similar[0]
    
    def convert_sentence_to_check(self, sentence):
        """Return string representation of the item order"""
        return f"{sentence.number} {sentence.adjetive} {sentence.noun}"
    
    def manage_replacement_amount(self, item_replaced):
        """Computes the number of the new item when no number is detected in the sentence"""
        if self.new_order_st.is_total_replace():
            self.new_order_st.number = item_replaced.number
        elif self.new_order_st.number == 0:
            self.new_order_st.number = 1
    
    def make_change(self):
        """Executes the check change"""
        # first we get which element to modify by noun similarity
        more_similar_item_id = self.get_more_similar_item_id()
        # then iterate over check items, modify requested item and add new one
        new_check = []
        for key, value in self.check_sts.items():
            item = value['obj']
            if key == more_similar_item_id:
                self.manage_replacement_amount(item)
                   
                if item.number - self.new_order_st.number > 0:
                    item.number -= self.new_order_st.number
                    new_check.append(self.convert_sentence_to_check(item))
            else:
                new_check.append(self.convert_sentence_to_check(item))

            
        new_check.append(self.convert_sentence_to_check(self.new_order_st))
                
        return new_check

# Main function    
def change_check(check, new_order):
    """Main function. Receives the check and new order, returns the new check.
        arguments: 
          string array -- the array with the order items
          string       -- the change requeriment 
        return: 
          string array -- the new check
    """
    order_manager = OrderManager(check, new_order)   
    new_check = order_manager.new_check

    return new_check


if __name__ == '__main__':
    check_arr = str(sys.argv[1]).split(',')
    new_check = change_check(check_arr, str(sys.argv[2]))
    print(f"New order: {new_check}")
