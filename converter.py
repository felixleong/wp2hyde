from lxml import etree
from datetime import datetime
import os
import slugify
import codecs

WPNS = {
    'excerpt': "http://wordpress.org/export/1.1/excerpt/",
    'content': "http://purl.org/rss/1.0/modules/content/",
    'wfw': "http://wellformedweb.org/CommentAPI/",
    'dc': "http://purl.org/dc/elements/1.1/",
    'wp': "http://wordpress.org/export/1.1/",
}
POSTS_DIR = 'blog/'
PAGES_DIR = 'page/'

class Post:
    """Blog post/page structure"""
    title = ''
    pub_date = None
    content = ''
    slug = ''
    tags = None


def create_dir(dir_name):
    """Create directory if it does not exists"""
    if not os.path.isdir(dir_name):
        os.makedirs(dir_name, 0755)


def save_post(file_name, post):
    """Save the post in Hyde's YAML format"""
    fhdl = codecs.open(file_name, 'w', 'utf-8')

    fhdl.write('---\n')

    title = post.title.replace('"', '\\"')
    fhdl.write(u'title: "{0}"\n'.format(title))

    timestamp = post.pub_date.strftime('%Y-%m-%d %H:%M:%S')
    fhdl.write(u'created: !!timestamp \'{0}\'\n'.format(timestamp))

    if len(post.tags) > 0:
        fhdl.write('tags:\n')
        for tag in post.tags:
            fhdl.write(u'    - {0}\n'.format(tag))

    fhdl.write('---\n\n')
    fhdl.write('{% mark post -%}')
    fhdl.write(post.content.strip())
    fhdl.write('{%- endmark %}')

    fhdl.close()


def main():
    """Main program"""
    with open('mytakeinlife.wordpress.2011-12-28.xml', 'r') as input_xml:
        parser = etree.XMLParser(ns_clean=True, remove_blank_text=True)
        tree = etree.parse(input_xml, parser)

        context = etree.iterwalk(tree, events=('start',), tag='item')
        for action, elem in context:
            post = Post()
            post.title = elem.find('title').text
            try:
                post.pub_date = datetime.strptime(elem.find('pubDate').text,
                        '%a, %d %b %Y %H:%M:%S +0000')
            except ValueError:
                post.pub_date = None
            post.content = elem.find('content:encoded', namespaces=WPNS).text
            post.slug = elem.find('wp:post_name', namespaces=WPNS).text
            if post.slug == '':
                post.slug = slugify.slugify(post.title)

            tag_elems = elem.findall('category[@domain="post_tag"]')
            post.tags = [ item.get('nicename') for item in tag_elems ]

            post_type = elem.find('wp:post_type', namespaces=WPNS).text
            status = elem.find('wp:status', namespaces=WPNS).text

            if status == 'publish':
                if post_type == 'post':
                    dir_name = POSTS_DIR + post.pub_date.strftime('%Y/%m/')
                elif post_type == 'page':
                    dir_name = PAGES_DIR
                else:
                    continue

                create_dir(dir_name)
                save_post(dir_name + post.slug + '.html', post)
                print u'{0} [{1}] - {2} @ {3}'.format(
                        post.title, post_type, status, post.pub_date)


if __name__ == '__main__':
    main()
