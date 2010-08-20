''' Models for treemenus '''

from itertools import chain

from django.db import models
from django.contrib.sites.models import Site
from django.utils.translation import ugettext_lazy
from django.utils.translation import ugettext as _

from ellington.core.models import BaseContentModel

class MenuItem(models.Model):
    ''' MenuItem class '''
    parent = models.ForeignKey('self', verbose_name=ugettext_lazy('Parent'),
                               null=True, blank=True)
    caption = models.CharField(ugettext_lazy('Caption'), max_length=50)
    url = models.CharField(ugettext_lazy('URL'), max_length=200, blank=True)
    named_url = models.CharField(ugettext_lazy('Named URL'), max_length=200,
                                 blank=True)
    level = models.IntegerField(ugettext_lazy('Level'), default=0,
                                editable=False)
    rank = models.IntegerField(ugettext_lazy('Rank'), default=0,
                               editable=False)
    menu = models.ForeignKey('Menu', related_name='contained_items',
                             verbose_name=ugettext_lazy('Menu'),
                             null=True, blank=True, editable=False)

    def __unicode__(self):
        ''' unicode representation '''
        return self.caption

    def save(self, force_insert=False, **kwargs):
        ''' save menu item '''

        from treemenus.utils import clean_ranks

        # Calculate level
        old_level = self.level
        if self.parent:
            self.level = self.parent.level + 1
        else:
            self.level = 0

        if self.pk:
            new_parent = self.parent
            old_parent = MenuItem.objects.get(pk=self.pk).parent
            if old_parent != new_parent:
                #If so, we need to recalculate the new ranks for the
                #item and its siblings (both old and new ones).
                if new_parent:
                    # Clean ranks for new siblings
                    clean_ranks(new_parent.children())
                    self.rank = new_parent.children().count()
                # Save menu item in DB. It has now officially changed parent.
                super(MenuItem, self).save(force_insert, **kwargs)
                if old_parent:
                    # Clean ranks for old siblings
                    clean_ranks(old_parent.children())
            else:
                # Save menu item in DB
                super(MenuItem, self).save(force_insert, **kwargs)

        # Saving the menu item for the first time (i.e creating the object)
        else:
            if not self.has_siblings():
                # No siblings - initial rank is 0.
                self.rank = 0
            else:
                # Has siblings - initial rank is highest sibling rank plus 1.
                siblings = self.siblings().order_by('-rank')
                self.rank = siblings[0].rank + 1
            super(MenuItem, self).save(force_insert, **kwargs)

        # If level has changed, force children to refresh their own level
        if old_level != self.level:
            for child in self.children():
                # Just saving is enough, it'll refresh its level correctly.
                child.save()

    def delete(self):
        ''' delete treemenu item '''

        from treemenus.utils import clean_ranks
        old_parent = self.parent
        super(MenuItem, self).delete()
        if old_parent:
            clean_ranks(old_parent.children())

    def caption_with_spacer(self):
        ''' caption '''
        spacer = ''
        for i in range(0, self.level):
            spacer += u'&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;'
        if self.level > 0:
            spacer += u'|-&nbsp;'
        return spacer + self.caption

    def get_flattened(self):
        ''' return flat structure '''

        flat_structure = [self]
        for child in self.children():
            flat_structure = chain(flat_structure, child.get_flattened())
        return flat_structure

    def siblings(self):
        ''' menu item siblings '''

        if not self.parent:
            return MenuItem.objects.none()
        else:
            # If menu item not yet been saved in DB (i.e does not have a pk yet)
            if not self.pk:
                return self.parent.children()
            else:
                return self.parent.children().exclude(pk=self.pk)

    def has_siblings(self):
        ''' number of siblings '''

        return self.siblings().count() > 0

    def children(self):
        ''' children of menu item '''

        _children = MenuItem.objects.filter(parent=self).order_by('rank',)
        for child in _children:
            # Hack to avoid unnecessary DB queries further down the track.
            child.parent = self
        return _children

    def has_children(self):
        ''' number of children '''

        return self.children().count() > 0


class Menu(BaseContentModel):
    name = models.CharField(ugettext_lazy('Name'), max_length=50)
    root_item = models.ForeignKey(MenuItem, related_name='is_root_item_of',
                                  verbose_name=ugettext_lazy('Root Item'),
                                  null=True, blank=True, editable=False)

    def save(self, force_insert=False, **kwargs):
        if not self.root_item:
            root_item = MenuItem()
            root_item.caption = _('Root')
            # If creating a new object (i.e does not have a pk yet)
            if not self.pk:
                # Save, so that it gets a pk
                super(Menu, self).save(force_insert, **kwargs)
                force_insert = False
            root_item.menu = self
            root_item.save() # Save, so that it gets a pk
            self.root_item = root_item
        super(Menu, self).save(force_insert, **kwargs)

    def delete(self):
        if self.root_item is not None:
            self.root_item.delete()
        super(Menu, self).delete()

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = _('Menu')
        verbose_name_plural = _('Menus')
        unique_together = (('originating_site', 'name'),)
