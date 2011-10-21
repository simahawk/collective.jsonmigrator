import os
import base64
from zope.interface import implements
from zope.interface import classProvides
from collective.transmogrifier.interfaces import ISectionBlueprint
from collective.transmogrifier.interfaces import ISection
from Products.Archetypes.interfaces import IBaseObject




class PlonearticleInnerContent(object):
    """
    """

    classProvides(ISectionBlueprint)
    implements(ISection)

    def __init__(self, transmogrifier, name, options, previous):
        self.previous = previous
        self.context = transmogrifier.context
        self.path = options['path']
        self.datafield_prefix = options.get('field-prefix', '_plonearticle_')
        self.fieldnames = ('files','images','links',)

    def __iter__(self):
        for item in self.previous:

            if not item['_type']=='PloneArticle':
                yield item
                continue

            self.pa_keys = []
            for i in self.fieldnames:
                key = self.datafield_prefix + i
                if key in item.keys():
                    self.pa_keys.append(key)

            if not self.pa_keys:
                yield item
                continue

            obj = self.context.unrestrictedTraverse(
                        item['_path'].lstrip('/'), None)

            # path doesn't exist
            if obj is None:
                yield item
                continue

            if IBaseObject.providedBy(obj):
                for key in self.pa_keys:
                    value = item[key]
                    if not value:
                        continue
                    fieldname = key[len(self.datafield_prefix):]
                    field = obj.getField(fieldname)
                    if field is None:
                        continue
                    field_value = []
                    for i in value:
                        fname = 'attached'+fieldname.title()[:-1] # say attachedImage
                        file_path = i[fname]
                        path = os.path.join(self.path,file_path)
                        if os.path.isfile(path):
                            f = open(path,'rb')
                            content = f.read()
                            f.close()
                            i[fname] = content
                            field_value.append(i)
                    field.set(obj,field_value)

            yield item


        def get_images(self, value):
            import ipdb;ipdb.set_trace()


        def get_files(self, value):
            pass

        def get_links(self, value):
            pass




