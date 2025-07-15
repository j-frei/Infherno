
def antonyms_substitute(input_text):
    # https://github.com/GEM-benchmark/NL-Augmenter/tree/main/nlaugmenter/transformations/antonyms_substitute
    from nlaugmenter.transformations.antonyms_substitute import AntonymsSubstitute
    tf = AntonymsSubstitute()
    return tf.generate(input_text)
