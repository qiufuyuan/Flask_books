#coding=utf-8
from flask import Flask, render_template, flash, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField,SubmitField
from wtforms.validators import DataRequired

import sys
reload(sys)
sys.setdefaultencoding('utf-8')

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:123456@localhost:3306/flask_books'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'qfy'

db = SQLAlchemy(app)

class Author(db.Model):
    __table__name = 'author'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(16), unique=True)

    #关系引用
    # books是给Author模型用的，author是给Book模型用的
    books = db.relationship('Book', backref='author')

    def __repr__(self):
        return 'Author %s' %self.name

class Book(db.Model):
    __table__name = 'books'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(16),unique=True)
    author_id = db.Column(db.Integer, db.ForeignKey('author.id')) #外籍关联 表名.主键

    def __repr__(self):
        return 'Book %s %s' %(self.name,self.author_id)

# 自定义表单类
class AuthorForm(FlaskForm):
    author = StringField('作者', validators=[DataRequired()])
    book = StringField('书籍', validators=[DataRequired()])
    submit = SubmitField('提交')

@app.route('/delete_author/<author_id>')
def delete_author(author_id):

    author = Author.query.get(author_id)
    if author:
        try:
            # 查询后直接删除
            book = Book.query.filter_by(author_id=author.id).first()
            if book:
                db.session.delete(book)
            db.session.delete(author)
            db.session.commit()
        except Exception as e:
            print e
            flash('删除作者出错')
            db.session.rollback()
    else:
        flash('找不到作者')
    return redirect(url_for('index'))

# 删除书籍 -->网页中删除 -->点击需要发送书籍的ID给删除书籍的路由 --> 路由需要接受参数
@app.route("/delete_book/<book_id>")
def delete_book(book_id):

    # 查询数据库，是否有该ID的书，如果有就删除，没有提示错误
    book = Book.query.get(book_id)
    if book:
        try:
            db.session.delete(book)
            db.session.commit()
        except Exception as e:
            print e
            flash('删除书籍出错')
            db.session.rollback()
    else:
        flash('书籍找不到')
    # 如何返回当前网址 -->重定向
    return redirect(url_for('index'))

@app.route('/', methods=['GET','POST'])
def index():
    # 创建自定义的表单类
    author_form = AuthorForm()

    '''
    验证逻辑
    1.调用wtf的函数实现验证
    2.验证通过获取数据
    3.判断作者是否存在
    4.如果作者存在，判断书籍是否存在，没有重复书籍就添加数据，如果重复，提示错误
    5.如果作者不存在，就添加作者和书籍
    6.验证不通过就提示错误
    '''

    # 1.调用wtf的函数实现验证
    if author_form.validate_on_submit():

        #2.验证通过获取数据
        author_name = author_form.author.data
        book_name = author_form.book.data

    #   3.判断作者是否存在
        author = Author.query.filter_by(name=author_name).first()

    #   4.如果作者存在
        if author:
            # 判断书籍是否存在
            book = Book.query.filter_by(name=book_name).first()
            if book:
                flash('已存在同名书籍')
            else:
                try:
                    new_book = Book(name=book_name, author_id=author.id)
                    db.session.add(new_book)
                    db.session.commit()
                except Exception as e:
                    print e
                    flash('添加书籍失败')
                    db.session.rollback()
        else:
            #5.如果作者不存在
            try:
                new_author = Author(name=author_name)
                db.session.add(new_author)
                db.session.commit()

                new_book = Book(name=book_name,author_id=new_author.id)
                db.session.add(new_book)
                db.session.commit()
            except Exception as e:
                print e
                flash('添加作者和书籍失败')
                db.session.rollback()
    else:
        if request.method == 'POST':
            flash('参数不全')
    # 查询所有作者信息
    authors = Author.query.all()

    return render_template('book.html', authors = authors, form = author_form)

if __name__ == '__main__':
    # db.drop_all()
    # db.create_all()
    #
    # au1 = Author(name='老王')
    # au2 = Author(name='小李')
    # au3 = Author(name='老刘')
    #
    # db.session.add_all([au1,au2,au3])
    # db.session.commit()
    #
    # bk1 = Book(name='老王回忆录', author_id=au1.id)
    # bk2 = Book(name='Python入门', author_id=au1.id)
    # bk3 = Book(name='Java入门', author_id=au2.id)
    # bk4 = Book(name='Spring入门', author_id=au3.id)
    #
    # db.session.add_all([bk1,bk2,bk3,bk4])
    # db.session.commit()


    app.run()
