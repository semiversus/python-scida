import os
import shutil
import yaml
import jinja2

class Page:
    def __init__(self, content:str, meta:dict):
        self.content=content
        self.meta=meta
    
    def __getitem__(self, key):
        return self.meta[key]
    
    def __getattr__(self, key):
        return self.meta[key]
    
    @classmethod
    def read_from_file(cls, filename:str):
        assert filename.endswith('.md')
        with open(filename) as f:
            meta_block = ''
            for line in f:
                if line.strip() == '':
                    break
                meta_block += line
        
            meta = yaml.load(meta_block)
            content = f.read()
        if 'path' not in meta:
            meta['path'] = filename
        if 'output_file' not in meta:
            meta['output_file'] = filename[8:-3] + '.html'
        return cls(content, meta)
    
    def __repr__(self):
        return self.path

def main():
    pages = []

    # read pages
    for cur_path, _, files in os.walk('content'):
        for file in files:
            if file.endswith('.md'):
                filepath = os.path.join(cur_path, file)
                page = Page.read_from_file(filepath)
                pages.append(page)

    # prepare output folder
    try:
        shutil.rmtree('output')
    except OSError:
        pass
    
    # copy static files
    shutil.copytree('template/static', 'output')

    # render pages
    env = jinja2.Environment(loader=jinja2.FileSystemLoader(os.getcwd()+'/template'))

    for page in pages:
        if 'template' not in page.meta:
            continue
        template = env.get_template(page.meta['template'])
        html_content = template.render(content=page.content, pages=pages, **page.meta)
        with open('output/' + page.meta['output_file'], 'w') as f:
            f.write(html_content)