import os
import shutil
import yaml
import jinja2
import markdown

SRC_PATH = 'content'
DST_PATH = 'output'

class File:
    def __init__(self, path:str):
        self.path=path
        self.path_abs = os.path.abspath(os.path.join(SRC_PATH, path))

        assert os.path.exists(self.path_abs)

    def has_extension(self, extension):
        return self.path.endswith(extension)

class Page:
    def __init__(self, filename:str):
        assert filename.endswith('.md')

        meta = {
            'template': None,
            'src_path': filename,
            'src_path_abs': os.path.join(SRC_PATH, filename),
            'dst_path': filename[:-3] + '.html',
            'dst_path_abs': os.path.join(DST_PATH, filename[:-3] + '.html'),
        }

        content, yaml_meta = Page._read_file(meta['src_path_abs'])

        meta.update(yaml_meta)

        self.content=content

        self._meta=meta

        for key, value in meta.items():  # make it accessible as attributes
            setattr(self, key, value)
    
    def __getitem__(self, key):
        return self._meta[key]

    @staticmethod
    def _read_file(filename:str):
        with open(filename) as f:
            meta_block = ''
            for line in f:
                if line.strip() == '':
                    break
                meta_block += line
        
            meta = yaml.load(meta_block)
            content = f.read()
        return content, meta
    
    def __repr__(self):
        return self['src_path']

def main():
    files = []
    pages = []

    # read pages
    for cur_path, directories, files_ in os.walk(SRC_PATH):
        for file_ in files_+directories:
            rel_path = os.path.relpath(cur_path, SRC_PATH)
            path=os.path.join(rel_path, file_)
            files.append(File(path))

    for file_ in files:
        if file_.has_extension('.md'):
            pages.append(Page(file_.path))

    # prepare output folder
    try:
        shutil.rmtree('output')
    except OSError:
        pass
    
    # copy static files
    shutil.copytree(os.path.join('template', 'static'), DST_PATH)

    # render pages
    md = markdown.Markdown(extensions=['meta'])
    template_path = os.path.join(os.getcwd(), 'template')
    env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_path))
    env.filters['markdown'] = lambda text: jinja2.Markup(md.convert(text))

    for page in pages:
        if page.template is None:
            continue
        template = env.get_template(page.template)
        html_content = template.render(content=page.content, pages=pages, **page._meta)
        with open(page.dst_path_abs, 'w') as f:
            f.write(html_content)