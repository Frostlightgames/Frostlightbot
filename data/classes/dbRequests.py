from Frostlightbot.data.functions.log import *
from Frostlightbot.data.classes.dbConnect import *
from Frostlightbot.data.classes.database import *

class dbRequests:

    def update_entry(self,table,id,**keys):

        session = get_session()

        try:
            entry = session.query(table).filter_by(id=id).first()

            if entry is None:
                log(ERROR,f"Id does not exist {entry}")
                return False

            for key, value in keys.items():
                if hasattr(entry,key):
                    setattr(entry,key,value)
                else:
                    log(ERROR,f"Key does not exist {key}")
            
            session.commit()
            return True

        except Exception as e:
            session.rollback()
            log(ERROR,f"Failed to update table entry {id} in table {table.__tablename__}: {e}")
            return False

        finally:
            session.close()
    
    def create_entry(self,table,**keys):

        session = get_session()

        try:
            entry = table(**keys)
            session.add(entry)
            session.commit()

        except Exception as e:
            session.rollback()
            log(ERROR, f"Failed to create entry in {table.__tablename__}: {e}")
            return False

        finally:
            session.close()

    def select_entry(self,table,*columns,**keys):

        session = get_session()

        try:
            if columns:
                data = session.query(*columns).filter_by(**keys).all()
            else:
                data = session.query(table).filter_by(**keys).all()

            if data == []:
                log(ERROR, f"No entry was found in {table.__tablename__}")
                return False
            else:
                return data

        except Exception as e:
            log(ERROR, f"Failed to select entry's in {table.__tablename__}: {e}")
            return False
        
        finally:
            session.close()


