
def backtranslate(input_text):
    # https://github.com/GEM-benchmark/NL-Augmenter/tree/main/nlaugmenter/transformations/back_translation
    from nlaugmenter.transformations.back_translation import BackTranslation
    tf = BackTranslation()
    return tf.generate(input_text)
