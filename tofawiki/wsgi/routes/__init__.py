from . import translate

def configure(config, bp):


    @bp.route('/')
    def root():
        return 'Hey, In order to use the service use tofawiki.wmflabs.org/translate/enwiki/Article_Name</br>' \
                'Source code in <a href="https://github.com/Ladsgroup/tofawiki">github</a>'

    bp = translate.configure(bp, config)
    return bp
