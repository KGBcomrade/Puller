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
                                'omega': 6.2,
                                'x': 12,
                                'L0': 2,
                                'alpha': -0.01,
                                'r0': 62.5,
                                'rw': 25,
                                'lw': 15,
                                'xv': 1,
                                'xa': .003,
                                'xd': .4,
                                'Lv': 8,
                                'La': 20,
                                'tW': 45,
                                'dr': .1,
                                'x0': 0}}}
        self.last = s['last']
        self.s = s['settings']

    def _returnSettings(dictr):
        return dictr['omegaType'], dictr.get('k', 7), dictr.get('omega', 6.2), dictr.get('x', 12), dictr.get('L0', 2), dictr.get('alpha', -0.01), dictr['r0'], dictr['rw'], dictr['lw'], dictr['xv'], dictr['xa'], dictr['xd'], dictr['Lv'], dictr['La'], dictr['tW'], dictr['dr'], dictr.get('x0', 0)

    def getLast(self):
        return SettingsLoader._returnSettings(self.s[self.last])
    
    def getNames(self):
        return self.s.keys()


    def _save(self):
        s = {'last': self.last, 'settings': self.s}
        with open(filePath, 'w') as f:
            json.dump(s, f, indent=4)
    
    def load(self, name):
        self.last = name
        self._save()     
        return SettingsLoader._returnSettings(self.s[name])

    def save(self, name, **kwargs):
        self.s[name] = kwargs
        self._save() 

