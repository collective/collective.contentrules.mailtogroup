from zope.i18nmessageid import MessageFactory

mailtogroupMessageFactory = MessageFactory('collective.contentrules.mailtogroup')


def initialize(context):
    """Intializer called when used as a Zope 2 product."""
