import spacy
import spacy.scorer
from prodigy.components.db import connect
from prodigy.core import recipe, recipe_args
from prodigy.models.ner import EntityRecognizer, merge_spans
from prodigy.util import log
from prodigy.components.preprocess import split_sentences, add_tokens


def gold_to_spacy(dataset, spacy_model, biluo=False):
    # Ripped from ner.gold_to_spacy. Only change is returning annotations instead of printing or saving
    DB = connect()
    examples = DB.get_dataset(dataset)
    examples = [eg for eg in examples if eg['answer'] == 'accept']
    if biluo:
        if not spacy_model:
            prints("Exporting annotations in BILUO format requires a spaCy "
                   "model for tokenization.", exits=1, error=True)
        nlp = spacy.load(spacy_model)
    annotations = []
    for eg in examples:
        entities = [(span['start'], span['end'], span['label'])
                    for span in eg.get('spans', [])]
        if biluo:
            doc = nlp(eg['text'])
            entities = spacy.gold.biluo_tags_from_offsets(doc, entities)
            annot_entry = [eg['text'], entities]
        else:
            annot_entry = [eg['text'], {'entities': entities}]
        annotations.append(annot_entry)

    return annotations


def evaluate_prf(ner_model, examples):
    # Source: https://stackoverflow.com/questions/44827930/evaluation-in-a-spacy-ner-model
    scorer = spacy.scorer.Scorer()
    for input_, annot in examples:
        doc_gold_text = ner_model.make_doc(input_)
        gold = spacy.gold.GoldParse(doc_gold_text, entities=annot['entities'])
        pred_value = ner_model(input_)
        scorer.score(pred_value, gold)
    return scorer.scores


@recipe("ner.stats",
        dataset=recipe_args["dataset"],
        spacy_model=recipe_args["spacy_model"],
        label=recipe_args["entity_label"],
        isPrf=("Output Precsion, Recall, F-Score", "flag", "prf"))
def model_stats(dataset, spacy_model, label=None, isPrf=False):
    """
    Evaluate model accuracy of model based on dataset with no training
    inspired from https://support.prodi.gy/t/evaluating-precision-and-recall-of-ner/193/2
    found on https://support.prodi.gy/t/evaluating-precision-and-recall-of-ner/193
    got basic model evaluation by looking at the batch-train recipe
    """

    log("RECIPE: Starting recipe ner.stats", locals())
    DB = connect()
    nlp = spacy.load(spacy_model)

    isPrf = 'True'
    if(isPrf):
        examples = gold_to_spacy(dataset, spacy_model)
        score = evaluate_prf(nlp, examples)
        print("Precision {:0.4f}\tRecall {:0.4f}\tF-score {:0.4f}".format(
            score['ents_p'], score['ents_r'], score['ents_f']))

    else:
        # ripped this from ner.batch-train recipe
        model = EntityRecognizer(nlp, label=label)
        evaldoc = merge_spans(DB.get_dataset(dataset))
        evals = list(split_sentences(model.orig_nlp, evaldoc))

        scores = model.evaluate(evals)

        print("Accuracy {:0.4f}\tRight {:0.0f}\tWrong {:0.0f}\tUnknown {:0.0f}\tEntities {:0.0f}".format(
            scores['acc'], scores['right'], scores['wrong'], scores['unk'], scores['ents']))
