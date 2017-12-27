# Created by aviade
# Time: 31/03/2016 09:15
from __future__ import print_function

import logging
import os
from datetime import datetime

from sqlalchemy import Boolean, Integer, Unicode
from sqlalchemy import Column, and_
from sqlalchemy import create_engine
from sqlalchemy import event
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import text
from sqlalchemy.sql.schema import ForeignKey

from commons import *
from config_class import getConfig

Base = declarative_base()

configInst = getConfig()

dialect_name = getConfig().get("DB", "dialect_name")

exec 'import ' + dialect_name

exec 'from ' + dialect_name + ' import DATETIME'

dt = eval(dialect_name).DATETIME(
    storage_format="%(year)04d-%(month)02d-%(day)02d %(hour)02d:%(minute)02d:%(second)02d",
    regexp=r"(\d{4})-(\d{2})-(\d{2}) (\d{2}):(\d{2}):(\d{2})",
)

domain = getConfig().get("DEFAULT", "domain")


class Author(Base):
    __tablename__ = 'authors'

    name = Column(Unicode, primary_key=True)
    domain = Column(Unicode, primary_key=True)
    author_guid = Column(Unicode, primary_key=True)

    author_screen_name = Column(Unicode, default=None)
    # author_full_name = Column(Unicode, default=None)
    author_osn_id = Column(Unicode, default=None)
    description = Column(Unicode, default=None)
    created_at = Column(Unicode, default=None)
    # statuses_count = Column(Integer, default=None)
    # followers_count = Column(Integer, default=None)
    # favourites_count = Column(Integer, default=None)
    # friends_count = Column(Integer, default=None)
    # listed_count = Column(Integer, default=None)
    # language = Column(Unicode, default=None)
    # profile_background_color = Column(Unicode, default=None)
    # profile_background_tile = Column(Unicode, default=None)
    # profile_banner_url = Column(Unicode, default=None)
    # profile_image_url = Column(Unicode, default=None)
    # profile_link_color = Column(Unicode, default=None)
    # profile_sidebar_fill_color = Column(Unicode, default=None)
    # profile_text_color = Column(Unicode, default=None)
    # default_profile = Column(Unicode, default=None)
    # contributors_enabled = Column(Unicode, default=None)
    # default_profile_image = Column(Unicode, default=None)
    # geo_enabled = Column(Unicode, default=None)
    # protected = Column(Boolean, default=None)
    # location = Column(Unicode, default=None)
    # notifications = Column(Unicode, default=None)
    # time_zone = Column(Unicode, default=None)
    # url = Column(Unicode, default=None)
    # utc_offset = Column(Unicode, default=None)
    # verified = Column(Unicode, default=None)
    # is_suspended_or_not_exists = Column(dt, default=None)
    #
    # # Tumblr fields
    # default_post_format = Column(Unicode, default=None)
    # likes_count = Column(Integer, default=None)
    # allow_questions = Column(Boolean, default=False)
    # allow_anonymous_questions = Column(Boolean, default=False)
    image_size = Column(Integer, default=None)

    media_path = Column(Unicode, default=None)

    author_type = Column(Unicode, default=None)

    # bad_actors_collector_insertion_date = Column(Unicode, default=None)
    # xml_importer_insertion_date = Column(Unicode, default=None)
    # vico_dump_insertion_date = Column(Unicode, default=None)
    # missing_data_complementor_insertion_date = Column(Unicode, default=None)
    # bad_actors_markup_insertion_date = Column(Unicode, default=None)
    # mark_missing_bad_actor_retweeters_insertion_date = Column(Unicode, default=None)
    # author_sub_type = Column(Unicode, default=None)
    # timeline_overlap_insertion_date = Column(Unicode, default=None)
    # original_tweet_importer_insertion_date = Column(Unicode, default=None)

    def __repr__(self):
        return "<Author(name='%s',domain='%s',author_guid='%s', statuses_count='%s')>" % (
            self.name, self.domain, self.author_guid, self.statuses_count)


class Post(Base):
    __tablename__ = 'posts'

    post_id = Column(Unicode, primary_key=True, index=True)
    author = Column(Unicode, default=None)
    guid = Column(Unicode, unique=True, default=None)
    title = Column(Unicode, default=None)
    url = Column(Unicode, unique=True, default=None)
    date = Column(dt, default=None)
    content = Column(Unicode, default=None)
    # description = Column(Unicode, default=None)
    is_detailed = Column(Boolean, default=True)
    is_LB = Column(Boolean, default=False)
    is_valid = Column(Boolean, default=True)
    domain = Column(Unicode, default=None)
    author_guid = Column(Unicode, default=None)

    media_path = Column(Unicode, default=None)

    # keywords = Column(Unicode, default=None)
    # paragraphs = Column(Unicode, default=None)
    post_osn_guid = Column(Unicode, default=None)
    post_type = Column(Unicode, default=None)
    # post_format = Column(Unicode, default=None)
    # reblog_key = Column(Unicode, default=None)
    # tags = Column(Unicode, default=None)
    # is_created_via_bookmarklet = Column(Boolean, default=None)
    # is_created_via_mobile = Column(Boolean, default=None)
    # source_url = Column(Unicode, default=None)
    # source_title = Column(Unicode, default=None)
    # is_liked = Column(Boolean, default=None)
    # post_state = Column(Unicode, default=None)
    #
    # post_osn_id = Column(Integer, default=None)
    # retweet_count = Column(Integer, default=None)
    # favorite_count = Column(Integer, default=None)
    created_at = Column(Unicode, default=None)

    # xml_importer_insertion_date = Column(Unicode, default=None)
    # timeline_importer_insertion_date = Column(Unicode, default=None)
    # original_tweet_importer_insertion_date = Column(Unicode, default=None)

    def __repr__(self):
        return "<Post(post_id='%s', guid='%s', title='%s', url='%s', date='%s', content='%s', author='%s', is_detailed='%s',  is_LB='%s',domain='%s',author_guid='%s')>" % (
            self.post_id, self.guid, self.title, self.url, self.date, self.content, self.author, self.is_detailed,
            self.is_LB, self.domain, self.author_guid)


class Target_Article(Base):
    __tablename__ = 'target_articles'

    post_id = Column(Unicode, ForeignKey('posts.post_id', ondelete="CASCADE"), primary_key=True)
    title = Column(Unicode, default=None)
    description = Column(Unicode, default=None)
    keywords = Column(Unicode, default=None)

    def __repr__(self):
        return "<TargetArticle(post_id='%s', title='%s', description='%s', keywords='%s')>" % (
            self.post_id, self.title, self.description, self.keywords)


# could be a 'paragraph' or caption
class Target_Article_Item(Base):
    __tablename__ = 'target_article_items'

    post_id = Column(Unicode, ForeignKey('posts.post_id', ondelete="CASCADE"), primary_key=True)
    type = Column(Unicode, default=None, primary_key=True)
    item_number = Column(Integer, default=None, primary_key=True)
    content = Column(Unicode, default=None)

    def __repr__(self):
        return "<Target_Article_Item(post_id='%s', type='%s', item_number='%s', content='%s')>" % (
            self.post_id, self.type, self.item_number, self.content)


class Text_From_Image(Base):
    __tablename__ = 'image_hidden_texts'

    post_id = Column(Unicode, ForeignKey('posts.post_id', ondelete="CASCADE"), primary_key=True)
    media_path = Column(Unicode, default=None)
    content = Column(Unicode, default=None)

    def __repr__(self):
        return "<Image_Hidden_Text(post_id='%s', media_path='%s', content='%s')>" % (
            self.post_id, self.media_path, self.content)


class Image_Tags(Base):
    __tablename__ = 'image_tags'

    post_id = Column(Unicode, ForeignKey('posts.post_id', ondelete="CASCADE"), primary_key=True)
    media_path = Column(Unicode, default=None)
    tags = Column(Unicode, default=None)

    def __repr__(self):
        return "<Image_Tags(post_id='%s', media_path='%s', tags='%s')>" % (
            self.post_id, self.media_path, self.tags)


class AuthorFeatures(Base):
    __tablename__ = 'author_features'
    author_guid = Column(Unicode, primary_key=True)
    window_start = Column(dt, primary_key=True)
    window_end = Column(dt, primary_key=True)
    attribute_name = Column(Unicode, primary_key=True)
    attribute_value = Column(Unicode)

    def __repr__(self):
        return "<AuthorFeatures(author_guid='%s', window_start='%s', window_end='%s', attribute_name='%s', attribute_value='%s')> " % (
            self.author_guid, self.window_start, self.window_end, self.attribute_name, self.attribute_value)

    def __init__(self, _author_guid=None, _window_start=None, _window_end=None, _attribute_name=None,
                 _attribute_value=None):
        self.author_guid = _author_guid
        self.window_start = _window_start
        self.window_end = _window_end
        self.attribute_name = _attribute_name
        self.attribute_value = _attribute_value


class Struct:
    def __init__(self, **entries): self.__dict__.update(entries)


class DB:
    '''
    Represents the primary blackboard of the system.
    The module must be the first one to setUp.
    '''

    def __init__(self):
        pass

    def setUp(self):
        configInst = getConfig()
        self._date = getConfig().eval(self.__class__.__name__, "start_date")
        self._pathToEngine = configInst.get(self.__class__.__name__, "DB_path") + \
                             configInst.get(self.__class__.__name__, "DB_name_prefix") + \
                             configInst.get("DEFAULT", "social_network_name") + \
                             configInst.get(self.__class__.__name__, "DB_name_suffix")

        start_date = configInst.get("DEFAULT", "start_date").strip("date('')")
        self._window_start = datetime.datetime.strptime(start_date, '%Y-%m-%d %H:%M:%S')
        self._window_size = datetime.timedelta(
            seconds=int(configInst.get("DEFAULT", "window_analyze_size_in_sec")))
        self._window_end = self._window_start + self._window_size

        if configInst.eval(self.__class__.__name__, "remove_on_setup"):
            self.deleteDB()

        self.engine = create_engine("sqlite:///" + self._pathToEngine, echo=False)
        self.Session = sessionmaker()
        self.Session.configure(bind=self.engine)

        self.session = self.Session()

        self.posts = "posts"
        self.authors = "authors"
        self.author_features = "author_features"

        @event.listens_for(self.engine, "connect")
        def connect(dbapi_connection, connection_rec):
            dbapi_connection.enable_load_extension(True)
            if getConfig().eval("OperatingSystem", "windows"):
                dbapi_connection.execute(
                    'SELECT load_extension("%s%s")' % (configInst.get("DB", "DB_path_to_extension"), '.dll'))
            if getConfig().eval("OperatingSystem", "linux"):
                dbapi_connection.execute(
                    'SELECT load_extension("%s%s")' % (configInst.get("DB", "DB_path_to_extension"), '.so'))

            dbapi_connection.enable_load_extension(False)

        if getConfig().eval(self.__class__.__name__, "dropall_on_setup"):
            Base.metadata.drop_all(self.engine)

        Base.metadata.create_all(self.engine)
        pass

    def tearDown(self):
        if getConfig().eval(self.__class__.__name__, "dropall_on_teardown"):
            if os.path.exists(self._pathToEngine):
                Base.metadata.drop_all(self.engine)

        if getConfig().eval(self.__class__.__name__, "remove_on_teardown"):
            self.deleteDB()

    def execute(self, window_start):
        pass

    def cleanUp(self, window_start):
        pass

    def canProceedNext(self, window_start):
        return True

    ##########################################################
    # miscellaneous
    def deleteDB(self):
        if os.path.exists(self._pathToEngine):
            try:
                os.remove(self._pathToEngine)
            except:
                logging.exception("Data Base %s remove failed" % self._pathToEngine)

    def commit(self):
        self.session.commit()

    def is_table_exist(self, table_name):
        q = "SELECT name FROM sqlite_master WHERE type='table' AND name=" + "\'" + table_name + "\'"
        query = text(q)
        result = self.session.execute(query)
        cursor = result.cursor
        records = list(cursor.fetchall())
        return len(records) != 0

    def update_query(self, query):
        self.session.execute(query)
        self.session.commit()

    ###########################################################
    # posts
    ###########################################################

    def delete_post(self, post_id):
        # delete_query = "DELETE FROM " + self.posts + " WHERE post_id=" + str(post_id)
        # self.session.execute(delete_query)
        # self.session.commit()

        self.session.query(Post).filter(Post.post_id == post_id).delete()
        self.session.commit()

    def get_all_posts(self):
        entries = self.session.query(Post).all()
        return entries

    def get_posts_by_domain(self, domain):
        posts_by_user = {}
        # posts = self.session.query(Post).filter(Post.domain == unicode(domain)).slice(start,stop).all()
        query = text("select posts.author_guid, posts.date, posts.content from posts where posts.domain = :domain "
                     "and length(posts.content)>0 and posts.date IS NOT NULL")
        counter = 0
        print("schema_definition.get_posts_by_domain before executing query..")
        result = self.session.execute(query, params=dict(domain=domain))
        print("schema_definition.get_posts_by_domain finished executing query..")
        cursor = result.cursor
        print("schema_definition.get_posts_by_domain before calling generator function")
        posts = self.result_iter(cursor, arraysize=10000)
        print("schema_definition.get_posts_by_domain after calling generator function")

        posts_by_user = self._create_user_posts_dictinary(posts)
        return posts_by_user

    def _create_user_posts_dictinary(self, posts):
        posts_by_user = {}
        counter = 0
        for current_post in posts:
            counter += 1
            if counter % 100 == 0:
                msg = "\r Creating post objects " + str(counter)
                print(msg, end="")
            str_date = current_post[1]
            date_obj = datetime.datetime.strptime(str_date, '%Y-%m-%d %H:%M:%S')
            post = Struct(author_guid=current_post[0], date=date_obj, content=current_post[2])

            if post.author_guid not in posts_by_user.keys():
                posts_by_user[str(post.author_guid)] = [post]
            else:
                posts_by_user[str(post.author_guid)].append(post)
        return posts_by_user

    def get_posts_by_author_guid(self, author_guid):

        query = self.session.query(Post).filter(Post.author_guid == author_guid).order_by(Post.date)
        entries = query.all()
        return entries


    def addPost(self, post):
        self.session.merge(post)

    def addPosts(self, posts):
        logging.info("total Posts inserted to DB: " + str(len(posts)))
        i = 1
        for post in posts:
            if i % 100 == 0:
                msg = "\r Insert post to DB: [{}".format(i) + "/" + str(len(posts)) + ']'
                print(msg, end="")
            i += 1
            self.addPost(post)
        self.session.commit()
        if len(posts) != 0: print("")

    def updatePost(self, post):
        self.session.query(Post).filter(Post.url == post[0]).update(post[1])

    def updatePosts(self, posts):
        logging.info("total Posts updated to DB: " + str(len(posts)))
        i = 1
        for post in posts:
            msg = "\r update post to DB: [{}".format(i) + "/" + str(len(posts)) + ']'
            print(msg, end="")
            i += 1
            self.updatePost(post)
        self.session.commit()
        if len(posts) != 0: print("")

    ###########################################################
    # authors
    ###########################################################

    def insert_or_update_authors_from_xml_importer(self, win_start, win_end):
        authors_to_update = []
        posts = self.session.query(Post).filter(Post.author_guid != u"").all()
        logging.info("Insert or update_authors from xml importer")
        logging.info("total Posts: " + str(len(posts)))
        i = 1
        for post in posts:
            msg = "\r Insert or update posts: [{}".format(i) + "/" + str(len(posts)) + ']'
            print(msg, end="")
            i += 1
            author_guid = post.author_guid
            domain = post.domain
            result = self.get_author_by_author_guid_and_domain(author_guid, domain)
            if not result:
                author = Author()
                author.name = post.author
                author.domain = post.domain
                author.author_guid = post.author_guid
            else:
                author = result[0]
            author.xml_importer_insertion_date = post.xml_importer_insertion_date
            authors_to_update.append(author)
        if len(posts) != 0: print("")
        self.add_authors(authors_to_update)

    def addAuthor(self, author):
        self.session.merge(author)

    def addAuthors(self, authorsList):
        logging.info("total Posts inserted to DB: " + str(len(authorsList)))
        i = 1
        for author in authorsList:
            if i % 100 == 0:
                msg = "\r Insert author to DB: [{}".format(i) + "/" + str(len(authorsList)) + ']'
                print(msg, end="")
            i += 1
            self.addAuthor(author)
        self.commit()

    def get_all_authors(self):
        result = self.session.query(Author).all()
        return result

    def get_authors_by_domain(self, domain):
        result = self.session.query(Author).filter(and_(Author.domain == unicode(domain)),
                                                   Author.author_osn_id.isnot(None)
                                                   ).all()

        return result

    def get_authors(self, domain):
        result = self.session.query(Author).filter(and_(Author.domain == unicode(domain),
                                                        Author.author_osn_id.isnot(None))
                                                   ).all()

        return result

    def get_number_of_targeted_osn_authors(self, domain):
        query = text("""SELECT COUNT(authors.author_guid)
                        FROM authors
                        WHERE authors.domain = :domain
                        AND authors.author_osn_id IS NOT NULL""")
        result = self.session.execute(query, params=dict(domain=domain))
        cursor = result.cursor
        tuples = cursor.fetchall()
        if tuples is not None and len(tuples) > 0:
            authors_count = tuples[0][0]
            return authors_count
        return None

    def get_number_of_authors(self):
        query = text("""SELECT COUNT(authors.author_guid)
                        FROM authors""")
        result = self.session.execute(query)
        cursor = result.cursor
        tuples = cursor.fetchall()
        if tuples is not None and len(tuples) > 0:
            authors_count = tuples[0][0]
            return authors_count
        return None

    def get_number_of_targeted_osn_posts(self, domain):
        query = text("""SELECT COUNT(posts.author_guid)
                        FROM posts
                        WHERE posts.domain = :domain""")
        result = self.session.execute(query, params=dict(domain=domain))
        cursor = result.cursor
        tuples = cursor.fetchall()
        if tuples is not None and len(tuples) > 0:
            posts_count = tuples[0][0]
            return posts_count
        return None

    def get_number_of_posts(self):
        query = text("""SELECT COUNT(posts.author_guid)
                        FROM posts""")
        result = self.session.execute(query)
        cursor = result.cursor
        tuples = cursor.fetchall()
        if tuples is not None and len(tuples) > 0:
            posts_count = tuples[0][0]
            return posts_count
        return None

    '''
    def get_author_by_id(self, author_id):

        query = self.session.query(Author).filter(Author.author_id == author_id)
        posts_result = query.all()

        #query = "SELECT * FROM " + self.posts + " WHERE post_id=" + str(post_id)
        #result = self.session.execute(query)
        #cursor = result.cursor
        #posts_result = cursor.fetchall()

        if len(posts_result):
            post = self.create_object(posts_result)
            return post
        return None
    '''

    def delete_author(self, name, domain, author_guid):
        self.session.query(Author).filter(
            (Author.name == name) & (Author.domain == domain) & (Author.author_guid == author_guid)).delete()
        self.session.commit()

    def update_author(self, author):
        self.session.merge(author)

    def get_author_name_by_post_content(self, post_content):
        query = text("select posts.author from posts where posts.content like :post_content")
        res = self.session.execute(query, params=dict(post_content=post_content + "%"))
        return [author_name[0] for author_name in res]

        ###########################################################
        # author_features
        ###########################################################

    def get_author_feature(self, author_guid, attribute_name):
        result = self.session.query(AuthorFeatures).filter(and_(AuthorFeatures.author_guid == author_guid,
                                                                AuthorFeatures.attribute_name == attribute_name)).all()
        if len(result) > 0:
            return result[0]
        return None

    def get_author_features(self):

        result = self.session.query(AuthorFeatures).all()
        if len(result) > 0:
            return result
        return None

    def get_author_features_labeled_authors_only(self):
        query = text('select author_features.*  \
                from  \
                  author_features  \
                inner join authors on (author_features.author_guid = authors.author_guid)  \
                where authors.author_type is not null')
        result = self.session.execute(query)
        cursor = result.cursor
        author_features = cursor.fetchall()
        return author_features

    def insert_authors_features(self, list_author_features):
        self.session.add_all(list_author_features)

    def update_author_features(self, author_features):
        self.session.merge(author_features)

    def update_target_articles(self, target_article):
        self.session.merge(target_article)

    def update_image_hidden_text(self, image_hidden_text):
        self.session.merge(image_hidden_text)

    def add_author_features(self, author_features):
        logging.info("total Author Features inserted to DB: " + str(len(author_features)))
        i = 1
        for author_feature in author_features:
            if i % 100 == 0:
                msg = "\r Insert author featurs to DB: [{}".format(i) + "/" + str(len(author_features)) + ']'
                print(msg, end="")
            i += 1
            self.update_author_features(author_feature)
        self.commit()

    def add_target_articles(self, target_articles):
        logging.info("target_articles inserted to DB: " + str(len(target_articles)))
        i = 1
        for target_article in target_articles:
            if i % 100 == 0:
                msg = "\r Insert target_article to DB: [{}".format(i) + "/" + str(len(target_articles)) + ']'
                print(msg, end="")
            i += 1
            self.update_target_articles(target_article)
        self.commit()

    def add_image_hidden_texts(self, image_hidden_texts):
        logging.info("image_hidden_texts inserted to DB: " + str(len(image_hidden_texts)))
        i = 1
        for image_hidden_text in image_hidden_texts:
            if i % 100 == 0:
                msg = "\r Insert image_hidden_text to DB: [{}".format(i) + "/" + str(len(image_hidden_texts)) + ']'
                print(msg, end="")
            i += 1
            self.update_image_hidden_text(image_hidden_text)
        self.commit()

    def delete_authors_features(self):
        q = text("delete from author_features")
        self.session.execute(q)
        self.commit()

    def delete_from_authors_features_trained_authors(self, author_guids_to_remove):
        self.session.query(AuthorFeatures).filter(AuthorFeatures.author_guid.in_(author_guids_to_remove)).delete(
            synchronize_session='fetch')
        self.session.commit()

    ###########################################################
    # key_authors
    ###########################################################
    def get_key_authors(self):
        query = text("SELECT author_name FROM export_key_authors")
        result = self.session.execute(query)
        cursor = result.cursor
        records = list(cursor.fetchall())
        return [rec[0] for rec in records]

    def is_export_key_authors_view_exist(self):
        query = text("SELECT name FROM sqlite_master WHERE type='view' AND name='export_key_authors'")
        result = self.session.execute(query)
        cursor = result.cursor
        records = list(cursor.fetchall())
        return len(records) != 0

    ###########################################################
    # authors
    ###########################################################

    def add_author(self, author):
        self.session.merge(author)

    def add_authors(self, authors):
        logging.info("-- add_authors --")
        logging.info("Number of authors is: " + str(len(authors)))
        i = 1
        for author in authors:
            msg = "\r Add author to DB: [{}".format(i) + "/" + str(len(authors)) + ']'
            print(msg, end="")
            i += 1
            self.add_author(author)
        self.commit()
        if len(authors) != 0: print("")

    def get_author_by_author_guid(self, author_guid):
        result = self.session.query(Author).filter(Author.author_guid == author_guid).all()
        return result

    def get_author_by_author_guid_and_domain(self, author_guid, domain):
        result = self.session.query(Author).filter(and_(Author.author_guid == author_guid,
                                                        Author.domain == domain)).all()
        return result

    def get_author_guid_to_author_dict(self):
        authors = self.get_all_authors()
        authors_dict = dict((aut.author_guid, aut) for aut in authors)
        return authors_dict

    def is_author_exists(self, author_guid, domain):
        author = self.get_author_by_author_guid_and_domain(author_guid, domain)
        return len(author) > 0


    def result_iter(self, cursor, arraysize=1000):
        'An iterator that uses fetchmany to keep memory usage down'
        while True:
            results = cursor.fetchmany(arraysize)
            if not results:
                break
            for result in results:
                yield result

    def update_authors_type_by_author_names(self, authors_name, author_type):
        logging.info("update_authors_type_by_author_names")
        query = 'UPDATE authors ' \
                'SET author_type = :author_type ' \
                'WHERE authors.name IN ' + "('" + "','".join(map(str, authors_name)) + "')"
        query = text(query)
        self.session.execute(query, params=dict(author_type=author_type))
        self.session.commit()

    def create_authors_index(self):
        logging.info("create_authors_index")
        query = "CREATE INDEX IF NOT EXISTS idx_authors " \
                "ON authors (domain, author_osn_id)"

        query = text(query)
        self.session.execute(query)
        self.session.commit()

    def create_posts_index(self):
        logging.info("create_authors_index")
        query = "CREATE INDEX IF NOT EXISTS idx_posts " \
                "ON posts (author_guid)"

        query = text(query)
        self.session.execute(query)
        self.session.commit()


    def get_labeled_authors_by_domain(self, domain):
        query = """
                SELECT authors.author_screen_name, authors.author_type
                FROM authors
                WHERE authors.domain = domain
                AND authors.author_type IS NOT NULL
                """
        query = text(query)

        result = self.session.execute(query, params=dict(domain=domain))
        cursor = result.cursor
        generator = self.result_iter(cursor)
        return generator

    def save_author_features(self, authors_features):
        print('\n Beginning merging author_features objects')
        counter = 0
        if authors_features:
            for author_features_row in authors_features:
                counter += 1
                self.update_author_features(author_features_row)
                if counter == 100:
                    print("\r " + "merging author-features objects", end="")
                    self.commit()
                    counter = 0
            if counter != 0:
                self.commit()
        print('Finished merging author_features objects')

    def create_posts_post_id_index(self):
        logging.info("create_posts_post_id_index")
        query = "CREATE INDEX IF NOT EXISTS create_posts_post_id_index " \
                "ON posts (posts)"


    def drop_unlabeled_predictions(self, predictions_table_name):
        query = "DROP TABLE IF EXISTS " + predictions_table_name + ";"
        query = text(query)
        self.session.execute(query)
        self.session.commit()

    def create_author_feature(self, author_guid, attribute_name, attribute_value):
        author_feature = AuthorFeatures()

        author_feature.author_guid = author_guid
        author_feature.attribute_name = attribute_name
        author_feature.attribute_value = unicode(attribute_value)
        author_feature.window_start = self._window_start
        author_feature.window_end = self._window_end

        msg = '\r adding ' + 'author_guid:' + author_guid + ' attribute_name: ' + attribute_name + ' attribute_value: ' + str(
            attribute_value)
        print(msg, end="")

        return author_feature

    def get_targeted_articles(self):
        targetd_articles = self.session.query(Target_Article).all()
        return targetd_articles

    def get_targeted_article_items(self):
        targetd_articles = self.session.query(Target_Article_Item).all()
        return targetd_articles

    def get_text_images(self):
        text_images = self.session.query(Text_From_Image).all()
        return text_images

    def get_authors_with_media(self):
        query = """SELECT authors.name, authors.media_path FROM authors
                    WHERE  authors.media_path IS NOT NULL"""
        query = text(query)
        result = self.session.execute(query)
        cursor = result.cursor
        tuples = self.result_iter(cursor)
        return tuples

    def get_authors_and_image_tags(self):
        query = """SELECT * FROM image_tags"""
        result = self.session.execute(query)
        cursor = result.cursor
        tuples = self.result_iter(cursor)
        return tuples

    def get_post_id_to_author_guid_mapping(self):
        query = """
                        SELECT posts.author_guid, posts.post_id 
                        FROM posts
                        """
        result = self.session.execute(query)
        cursor = result.cursor
        records = self.result_iter(cursor)
        records = list(records)

        return {record[1]: record[0] for record in records}

    def get_author_guid_word_embedding_vector_dict(self, table_name, targeted_field_name, word_embedding_type):
        query = self._get_author_guid_word_embedding_vector_full_query(table_name, targeted_field_name,
                                                                       word_embedding_type)
        result = self.session.execute(query, params=dict(table_name=table_name, targeted_field_name=targeted_field_name,
                                                         word_embedding_type=word_embedding_type))
        return self._create_author_guid_word_embedding_vector_dict_by_query(result)

    def _get_author_guid_word_embedding_vector_full_query(self, table_name, targeted_field_name, word_embedding_type):
        query = """
                SELECT *
                FROM author_word_embeddings
                WHERE table_name = :table_name
                AND targeted_field_name = :targeted_field_name
                AND word_embedding_type = :word_embedding_type
                AND author_id IS NOT NULL
                """
        return query

    def _create_author_guid_word_embedding_vector_dict_by_query(self, result):
        cursor = result.cursor
        records = self.result_iter(cursor)
        # records = list(records)
        author_guid_word_embedding_vector = {}
        for record in records:
            author_guid = record[0]
            selected_table_name = record[1]
            selected_targeted_field_name = record[3]
            selected_word_embedding_type = record[4]
            vector = record[5:]
            # vector_str = np.array(vector_str)
            # vector = vector_str.astype(np.float)
            author_guid_word_embedding_vector[author_guid] = vector
        return author_guid_word_embedding_vector


    def get_targeted_records_by_id_targeted_field_and_table_name(self, id_field, targeted_field_name, table_name,
                                                                 where_clauses):
        query = (
            "                SELECT {0}, {1}\n"
            "                FROM {2}\n"
            "                ").format(id_field, targeted_field_name, table_name)

        is_first_condition = False
        for where_clause_dict in where_clauses:
            field_name = where_clause_dict['field_name']
            value = where_clause_dict['value']
            if not is_first_condition:
                condition_clause = """
                                    WHERE {0} = {1}
                                    """.format(field_name, value)
                is_first_condition = True
            else:
                condition_clause = """
                                    AND {0} = {1}
                                    """.format(field_name, value)
            query += condition_clause
        query = text(query)
        result = self.session.execute(query)
        cursor = result.cursor
        tuples = self.result_iter(cursor)
        return tuples

    def get_word_vector_dictionary(self, table_name):
        query = """
                SELECT *
                FROM {0}
                """.format(table_name)
        query = text(query)
        result = self.session.execute(query)
        cursor = result.cursor
        tuples = self.result_iter(cursor)

        word_vector_dict = {}
        for tuple in tuples:
            word = tuple[0]
            vector = tuple[1:]
            # vector_str = np.array(vector_str)
            # vector = vector_str.astype(np.float)
            word_vector_dict[word] = vector
        return word_vector_dict

    def get_item_by_targeted_fields_dict_and_id(self, targeted_fields_dict, id_val):
        query = "SELECT * FROM " + targeted_fields_dict['table_name'] + " where " + targeted_fields_dict[
            'id_field'] + " = " + id_val
        result = self.session.execute(query)
        cursor = result.cursor

        result = cursor.fetchall()[0]
        return result

    def get_dict_idfield_to_item(self, targeted_fields_dict):
        id_field = targeted_fields_dict['id_field']
        query = 'select * from ' + targeted_fields_dict['table_name']
        answer = self.session.execute(text(query))
        return dict((getattr(item, id_field), item) for item in self.result_iter(answer))

    def get_author_id_by_field_id(self, field_id, id_val):
        if field_id == "post_id":
            query = 'SELECT author_guid FROM posts WHERE post_id=' + id_val
            answer = self.session.execute(text(query))
            cursor = answer.cursor
            result = cursor.fetchall()[0]
            return result[0]
        if field_id == "author_guid":
            return id_val
