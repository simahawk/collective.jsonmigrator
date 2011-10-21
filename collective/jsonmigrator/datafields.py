import os
import base64

from zope.interface import implements
from zope.interface import classProvides

from collective.transmogrifier.interfaces import ISectionBlueprint
from collective.transmogrifier.interfaces import ISection

from Products.Archetypes.interfaces import IBaseObject


class DataFields(object):
    """
    """

    classProvides(ISectionBlueprint)
    implements(ISection)

    def __init__(self, transmogrifier, name, options, previous):
        self.previous = previous
        self.context = transmogrifier.context
        self.path = options.get('path','')
        self.datafield_prefix = options.get('datafield-prefix', '_datafield_')
        self.root_path_length = len(self.context.getPhysicalPath())
        self.check_for_acquisition = int(options.get('acquisition-check', 0))

    def __iter__(self):
        for item in self.previous:

            # not enough info
            if '_path' not in item:
                yield item
                continue

            obj = self.context.unrestrictedTraverse(
                        item['_path'].lstrip('/'), None)

            # path doesn't exist
            if obj is None:
                yield item
                continue

            # I don't know why this sometimes doesn't work
            # so I added an option to skip this check on demand
            if self.check_for_acquisition:
                # do nothing if we got a wrong object through acquisition
                path = item['_path']
                if path.startswith('/'):
                    path = path[1:]
                if '/'.join(obj.getPhysicalPath()[self.root_path_length:]) != path:
                    yield item
                    continue

            if IBaseObject.providedBy(obj):
                for key in item.keys():

                    if not key.startswith(self.datafield_prefix):
                        continue

                    fieldname = key[len(self.datafield_prefix):]
                    field = obj.getField(fieldname)
                    if field is None:
                        continue
                    value = item[key]

                    if isinstance(value,dict) and value.get('data'):
                        value = base64.b64decode(value['data'])
                    elif isinstance(value,basestring):
                        path = os.path.join(self.path,value)
                        if os.path.isfile(path):
                            f = open(path,'rb')
                            value = f.read()
                            f.close()
                        else:
                            raise LookupError("Can't find path %s" % path)

                    # XXX: handle other data field implementations
                    old_value = field.get(obj)
                    if hasattr(old_value,'data'):
                        old_value = old_value.data
                    if value != old_value:
                        field.set(obj, value)
                        if isinstance(value,dict):
                            if 'filename' in value.keys():
                                obj.setFilename(value['filename'])
                            if 'content_type' in value.keys():
                                obj.setContentType(value['content_type'])

            yield item

