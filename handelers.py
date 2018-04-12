import tornado.web
import os
import tornado.ioloop
import tornado.log
import queries

from jinja2 import \
  Environment, PackageLoader, select_autoescape
  
ENV = Environment(
  loader=PackageLoader('blog', 'templates'),
  autoescape=select_autoescape(['html', 'xml'])
)

def initialize(self):
    self.session = queries.Session(
    'postgresql://postgres@localhost:5432/blog')

class TemplateHandler(tornado.web.RequestHandler):
  def render_template (self, tpl, context):
    template = ENV.get_template(tpl)
    self.write(template.render(**context))
    
    
class MainHandler(TemplateHandler):
    def initialize(self):
      self.session = queries.Session(
      'postgresql://postgres@localhost:5432/blog')
    def get (self):
      posts = self.session.query('SELECT * FROM post')
      self.render_template("index.html", {'posts': posts})
      
class PostHandler(TemplateHandler):
  def initialize(self):
      self.session = queries.Session(
      'postgresql://postgres@localhost:5432/blog')
  def get (self, slug):
    posts = self.session.query(
      'SELECT * FROM post WHERE slug = \'{}\''.format(slug),
      {'slug': slug}
    )
    self.render_template("post.html", {'post': posts[0]})

def make_app():
  return tornado.web.Application([
    (r"/", MainHandler),
    (r"/post/(.*)", PostHandler),
    (r"/static/(.*)", 
      tornado.web.StaticFileHandler, {'path': 'static'}),
  ], autoreload=True)
  
if __name__ == "__main__":
  tornado.log.enable_pretty_logging()
  app = make_app()
  app.listen(int(os.environ.get('PORT', '8080')))
  tornado.ioloop.IOLoop.current().start()