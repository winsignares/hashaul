from config import app, db, ma

class Task(db.Model):
    __tablename__ = 'tblTaks'

    id = db.Column(db.Integer, primary_key=True)
    nametaks = db.Column(db.String(50))
    id_user_fk = db.Column(db.Integer, db.ForeignKey('tblusers.id'))
    id_category_fk = db.Column(db.Integer, db.ForeignKey('tblcategory.id'))

    def __init__(self, nametaks, id_user_fk, id_category_fk):
        self.nametaks = nametaks
        self.id_user_fk = id_user_fk
        self.id_category_fk = id_category_fk

with app.app_context():
    db.create_all()

class CategorySchema(ma.Schema):
    class Meta:
        fields = ('id', 'namecategory')