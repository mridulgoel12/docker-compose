from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://user:super-secret-password@db:5432/test'
db = SQLAlchemy(app)

class Moment(db.Model):
    __tablename__ = 'moments'
    mid = db.Column('id', db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=False, nullable=False)

    def __repr__(self):
        return f'<Moment {self.name} parent_id:{self.parent_id}>'

Moment.parent_id = db.Column(db.Integer, db.ForeignKey(Moment.mid))
Moment.parent = relationship(Moment, backref='children', remote_side=Moment.mid)

@app.route('/')
def index():
    mid = request.args.get('id', default=1)
    return str(db.session.get(Moment, mid))

def format_descendants(moment, level=0):
    """Recursively format the descendants of a Moment."""
    indent = '&nbsp;' * 4 * level
    result = [f"{indent}{moment.name}"]
    for child in moment.children:
        result.extend(format_descendants(child, level + 1))
    return result

@app.route('/moments/<int:mid>/descendants')
def descendants(mid):
    parent = db.session.get(Moment, mid)
    if not parent:
        return f"No moment found with id {mid}", 404
    # Get the formatted descendants
    descendants_list = format_descendants(parent)
    return '<br>'.join(descendants_list)

with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(host='0.0.0.0')