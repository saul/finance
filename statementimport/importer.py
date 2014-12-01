from datetime import datetime


class BaseImporter:
    processors = []

    def process(self, line, **extra_fields):
        for processor_cls in self.processors:
            match = processor_cls.pattern.match(line)

            if not match:
                continue

            return processor_cls(match, line, extra_fields)

    @classmethod
    def processor(cls, processor_cls):
        cls.processors.append(processor_cls)
        return processor_cls


class BaseProcessor:
    transaction_class = None
    pattern = None

    def __init__(self, match, line, extra_fields):
        self.match = match
        self.line = line
        self.transaction = None
        self.process(extra_fields)

    def process(self, extra_fields):
        groups = self.match.groupdict()
        fields = extra_fields

        for group, value in groups.items():
            if value is not None:
                if group.startswith('date'):
                    try:
                        value = datetime.strptime(value, '%d-%m-%Y')
                    except ValueError:
                        value = datetime.strptime(value, '%Y-%m-%d')
                elif group == 'amount':
                    value = parse_currency(value)

            fields[group] = value

        fields = self.clean_fields(fields)
        self.transaction = self.transaction_class(**fields)

    def clean_fields(self, fields):
        return fields
