from config import app, db, ma

class Category(db.Model):
    __tablename__ = 'tblcategory'

    id = db.Column(db.Integer, primary_key=True)
    namecategory = db.Column(db.String(100))

    def __init__(self, namecategory):
        self.namecategory = namecategory

with app.app_context():
    db.create_all()

class CategorySchema(ma.Schema):
    class Meta:
        fields = ('id', 'namecategory')