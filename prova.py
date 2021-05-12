import re

def extract_coinpct (inputpreference, user_dict):
    substr = inputpreference.split('@')
    print(substr)
    print(substr[0])
    print(float(re.findall('-{0,1}[0-9]+\.{0,1}[0-9]*%{0,1}', substr[1]).pop().rstrip('%')))
    if re.match('-{0,1}[0-9]+\.{0,1}[0-9]*%{0,1}', substr[1].replace(' ','')):
        foundpct = float(re.findall('-{0,1}[0-9]+\.{0,1}[0-9]*%{0,1}', substr[1]).pop().rstrip('%'))
        user_dict[substr[0].replace(' ','')] = foundpct
    elif re.match('-{0,1}[0-9]+,{0,1}[0-9]*%{0,1}', substr[1].replace(' ','')): #changes only a comma from previous 
        foundpct = float(re.findall('-{0,1}[0-9]+,{0,1}[0-9]*%{0,1}', substr[1]).pop().rstrip('%'))
        user_dict[substr[0].replace(' ','')] = foundpct
    else:
        return ValueError 
    return user_dict



def response (samplestring):
    user_preferences = dict()
    if ';' in samplestring:
        samplestring = samplestring.split(';')
        print(samplestring)
        for preference in samplestring:
            try:
                user_preferences = extract_coinpct(preference,user_preferences)
            except:
                return ('Please start over. Type your preferences with the correct syntax')
        print(user_preferences)
        return ('Preferences correctly imported!')
    else:
        try:
            user_preferences = extract_coinpct(preference,user_preferences)
        except:
            return ('Please start over. Type your preferences with the correct syntax -------')
        return ('Preferences correctly imported!')

samplestring = 'bitcoin   @  -3.5%   ; ethereum@45%'
print(response(samplestring))
