import json

filePath = 'misc/settings.json'

_defaultSetting = {
    'omegaType': 'theta',
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
    'x0': 0
}

class Settings:
    def __init__(self, **kwargs):
        for kp in _defaultSetting.items():
            self.__dict__.setdefault(*kp)
        self.__dict__.update(kwargs)

class SettingsLoader:
    def __init__(self):
        try:
            with open(filePath, 'r') as f:
                s = json.load(f)
        except FileNotFoundError:
            s = {'last': 'default',
                'settings': {
                    'default': _defaultSetting
                    }}
        self.last = s['last']
        self.s = s['settings']

    def getLast(self) -> Settings:
        return Settings(**self.s[self.last])
    
    def getNames(self):
        return self.s.keys()


    def _save(self):
        s = {'last': self.last, 'settings': self.s}
        with open(filePath, 'w') as f:
            json.dump(s, f, indent=4)
    
    def load(self, name) -> Settings:
        self.last = name
        self._save()     
        return Settings(**self.s[name])

    def save(self, name, settings: Settings):
        self.s[name] = settings.__dict__
        self._save() 

