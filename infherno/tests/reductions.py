
def abbreviate(input_text):
    # https://github.com/GEM-benchmark/NL-Augmenter/tree/main/nlaugmenter/transformations/abbreviation_transformation
    from nlaugmenter.transformations.abbreviation_transformation import Abbreviate
    tf = Abbreviate()
    return tf.generate(input_text)
