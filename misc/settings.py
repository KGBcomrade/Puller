import json

filePath = 'misc/settings.json'

class SettingsLoader:
    def __init__(self):
        try:
            with open(filePath, 'r') as f:
                s = json.load(f)
        except FileNotFoundError:
            s = {'last': 'default',
                'settings': {
                    'default': {'omegaType': 'theta',
                                'k': 7,
                                'r0': 62.5,
                                'rw': 25,
                                'lw': 15,
                                'xv': 1,
                                'xa': .003,
                                'xd': .4,
                                'Lv': 8,
                                'La': 20,
                                'tW': 45,
                                'dr': .1}}}
        self.last = s['last']
        self.s = s['settings']

    def _returnSettings(dictr):
        return dictr['omegaType'], dictr['k'], dictr['r0'], dictr['rw'], dictr['lw'], dictr['xv'], dictr['xa'], dictr['xd'], dictr['Lv'], dictr['La'], dictr['tW'], dictr['dr']

    def getLast(self):
        return SettingsLoader._returnSettings(self.s[self.last])
    
    def getNames(self):
        return self.s.keys()


    def _save(self):
        s = {'last': self.last, 'settings': self.s}
        with open(filePath, 'w') as f:
            json.dump(s, f)
    
    def load(self, name):
        self.last = name
        self._save()     
        return SettingsLoader._returnSettings(self.s[name])

    def save(self, name, omegaType, k, r0, rw, lw, xv, xa, xd, Lv, La, tW, dr):
        self.s[name] = {'omegaType': omegaType, 'k': k, 'r0': r0, 'rw': rw, 'lw': lw, 'xv': xv, 'xa': xa, 'xd': xd, 'Lv': Lv, 'La': La, 'tW': tW, 'dr': dr}
        self._save() 

