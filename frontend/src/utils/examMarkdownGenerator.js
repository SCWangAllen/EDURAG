/**
 * Exam Markdown Generator
 *
 * Pure functions for generating Markdown-formatted exam papers and answer sheets.
 * Extracted from Questions.vue — no Vue reactivity dependencies.
 */

export const generateSingleChoiceQuestions = (questions, startNumber) => {
  return questions.map((q, index) => {
    const questionNum = startNumber + index
    let questionText = `**${questionNum}.** ${q.content || 'Question content missing'}\n\n`

    if (q.options && q.options.length > 0) {
      q.options.forEach(option => {
        questionText += `   ${option}\n`
      })
    } else {
      questionText += `   (Options missing)\n`
    }

    questionText += `\n`
    return questionText
  }).join('')
}

export const generateClozeQuestions = (questions, startNumber) => {
  return questions.map((q, index) => {
    const questionNum = startNumber + index
    return `**${questionNum}.** ${q.content || 'Question content missing'}\n\n`
  }).join('')
}

export const generateShortAnswerQuestions = (questions, startNumber) => {
  return questions.map((q, index) => {
    const questionNum = startNumber + index
    return `**${questionNum}.** ${q.content || 'Question content missing'}\n\n<br><br><br>\n\n`
  }).join('')
}

export const generateAutoQuestions = (questions, startNumber) => {
  return questions.map((q, index) => {
    const questionNum = startNumber + index
    let questionText = `**${questionNum}.** ${q.content || 'Question content missing'}\n\n`

    if (Array.isArray(q.options) && q.options.length > 0) {
      const optionLabels = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']
      q.options.forEach((option, optIndex) => {
        if (option && option.trim()) {
          questionText += `   ${optionLabels[optIndex]}. ${option}\n`
        }
      })
      questionText += `\n`
    } else {
      questionText += `\n<br><br>\n`
    }

    return questionText
  }).join('')
}

export const generateAnswerSheet = (questionsByType) => {
  let answerSheet = `\n---\n\n# 📋 Answer Sheet\n\n**Name:** ________________　**Student ID:** ________________　**Class:** ________________\n\n`

  let questionNumber = 1

  if (questionsByType.single_choice.length > 0) {
    answerSheet += `## Part I: Multiple Choice Answers\n\n`

    const singleChoiceCount = questionsByType.single_choice.length
    let tableRows = []

    for (let i = 0; i < singleChoiceCount; i += 5) {
      const rowQuestions = []
      const rowAnswers = []

      for (let j = 0; j < 5 && (i + j) < singleChoiceCount; j++) {
        const qNum = questionNumber + i + j
        rowQuestions.push(`${qNum}`)
        rowAnswers.push('____')
      }

      tableRows.push(`| ${rowQuestions.join(' | ')} |`)
      tableRows.push(`| ${rowAnswers.join(' | ')} |`)

      if (i === 0) {
        tableRows.splice(1, 0, `|${'---|'.repeat(rowQuestions.length)}`)
      }

      tableRows.push('')
    }

    answerSheet += tableRows.join('\n') + '\n'
    questionNumber += singleChoiceCount
  }

  if (questionsByType.cloze.length > 0) {
    answerSheet += `## Part II: Fill-in-the-Blank Answers\n\n`
    questionsByType.cloze.forEach((q, index) => {
      const qNum = questionNumber + index
      answerSheet += `**${qNum}.** ________________________\n\n`
    })
    questionNumber += questionsByType.cloze.length
  }

  if (questionsByType.short_answer.length > 0) {
    answerSheet += `## Part III: Short Answer Responses\n\n`
    questionsByType.short_answer.forEach((q, index) => {
      const qNum = questionNumber + index
      answerSheet += `**${qNum}.** \n\n<br><br><br><br>\n\n`
    })
    questionNumber += questionsByType.short_answer.length
  }

  if (questionsByType.auto.length > 0) {
    answerSheet += `## Part IV: Auto-Generated Question Answers\n\n`
    questionsByType.auto.forEach((q, index) => {
      const qNum = questionNumber + index
      if (Array.isArray(q.options) && q.options.length > 0) {
        answerSheet += `**${qNum}.** ____\n\n`
      } else if (q.original_type === 'cloze' || q.type === 'cloze') {
        answerSheet += `**${qNum}.** ________________________\n\n`
      } else {
        answerSheet += `**${qNum}.** \n`
        answerSheet += `${'_'.repeat(50)}\n\n${'_'.repeat(50)}\n\n`
      }
    })
  }

  answerSheet += `\n---\n\n# 🔑 Answer Key (For Instructor Reference)\n\n`

  let answerNumber = 1

  if (questionsByType.single_choice.length > 0) {
    answerSheet += `## Multiple Choice Answer Key\n\n`
    questionsByType.single_choice.forEach((q, index) => {
      answerSheet += `**${answerNumber + index}.** ${q.correct_answer}\n`
      if (q.explanation) {
        answerSheet += `   *Explanation: ${q.explanation}*\n`
      }
      answerSheet += '\n'
    })
    answerNumber += questionsByType.single_choice.length
  }

  if (questionsByType.cloze.length > 0) {
    answerSheet += `## Fill-in-the-Blank Answer Key\n\n`
    questionsByType.cloze.forEach((q, index) => {
      answerSheet += `**${answerNumber + index}.** ${q.correct_answer}\n`
      if (q.explanation) {
        answerSheet += `   *Explanation: ${q.explanation}*\n`
      }
      answerSheet += '\n'
    })
    answerNumber += questionsByType.cloze.length
  }

  if (questionsByType.short_answer.length > 0) {
    answerSheet += `## Short Answer Reference Answers\n\n`
    questionsByType.short_answer.forEach((q, index) => {
      answerSheet += `**${answerNumber + index}.** ${q.correct_answer}\n`
      if (q.explanation) {
        answerSheet += `   *Notes: ${q.explanation}*\n`
      }
      answerSheet += '\n'
    })
    answerNumber += questionsByType.short_answer.length
  }

  if (questionsByType.auto.length > 0) {
    answerSheet += `## Auto-Generated Question Answer Key\n\n`
    questionsByType.auto.forEach((q, index) => {
      answerSheet += `**${answerNumber + index}.** ${q.correct_answer}\n`
      if (q.explanation) {
        answerSheet += `   *Explanation: ${q.explanation}*\n`
      }
      answerSheet += '\n'
    })
  }

  return answerSheet
}

export const generateCustomAnswerSheet = (questionsByType, styles) => {
  let answerSheet = `\n---\n\n# ${styles.answerSheet.title}\n\n${styles.answerSheet.studentInfo}\n\n`

  let questionNumber = 1

  if (styles.answerSheet.format === 'table') {
    if (questionsByType.single_choice && questionsByType.single_choice.length > 0) {
      answerSheet += `## Part I: Multiple Choice Answers\n\n`

      const singleChoiceCount = questionsByType.single_choice.length
      let tableRows = []

      for (let i = 0; i < singleChoiceCount; i += 5) {
        const rowQuestions = []
        const rowAnswers = []

        for (let j = 0; j < 5 && (i + j) < singleChoiceCount; j++) {
          const qNum = questionNumber + i + j
          rowQuestions.push(`${qNum}`)
          rowAnswers.push('____')
        }

        tableRows.push(`| ${rowQuestions.join(' | ')} |`)
        tableRows.push(`| ${rowAnswers.join(' | ')} |`)

        if (i === 0) {
          tableRows.splice(1, 0, `|${'---|'.repeat(rowQuestions.length)}`)
        }

        tableRows.push('')
      }

      answerSheet += tableRows.join('\n') + '\n'
      questionNumber += singleChoiceCount
    }
  } else if (styles.answerSheet.format === 'list') {
    if (questionsByType.single_choice && questionsByType.single_choice.length > 0) {
      answerSheet += `## Multiple Choice Answers\n\n`
      questionsByType.single_choice.forEach((q, index) => {
        const qNum = questionNumber + index
        answerSheet += `${qNum}. ____\n`
      })
      answerSheet += '\n'
      questionNumber += questionsByType.single_choice.length
    }
  } else if (styles.answerSheet.format === 'grid') {
    if (questionsByType.single_choice && questionsByType.single_choice.length > 0) {
      answerSheet += `## Multiple Choice Grid\n\n`
      answerSheet += `| Q# | A | B | C | D | Answer |\n`
      answerSheet += `|----|---|---|---|---|--------|\n`
      questionsByType.single_choice.forEach((q, index) => {
        const qNum = questionNumber + index
        answerSheet += `| ${qNum} | ○ | ○ | ○ | ○ | ____ |\n`
      })
      answerSheet += '\n'
      questionNumber += questionsByType.single_choice.length
    }
  }

  if (questionsByType.cloze && questionsByType.cloze.length > 0) {
    answerSheet += `## Fill-in-the-Blank Answers\n\n`
    questionsByType.cloze.forEach((q, index) => {
      const qNum = questionNumber + index
      answerSheet += `**${qNum}.** ________________________\n\n`
    })
    questionNumber += questionsByType.cloze.length
  }

  if (questionsByType.short_answer && questionsByType.short_answer.length > 0) {
    answerSheet += `## Short Answer Responses\n\n`
    questionsByType.short_answer.forEach((q, index) => {
      const qNum = questionNumber + index
      answerSheet += `**${qNum}.** \n\n<br><br><br><br>\n\n`
    })
    questionNumber += questionsByType.short_answer.length
  }

  if (questionsByType.auto && questionsByType.auto.length > 0) {
    answerSheet += `## Auto-Generated Question Answers\n\n`
    questionsByType.auto.forEach((q, index) => {
      const qNum = questionNumber + index
      if (Array.isArray(q.options) && q.options.length > 0) {
        answerSheet += `**${qNum}.** ____\n\n`
      } else if (q.original_type === 'cloze' || q.type === 'cloze') {
        answerSheet += `**${qNum}.** ________________________\n\n`
      } else {
        answerSheet += `**${qNum}.** \n`
        answerSheet += `${'_'.repeat(50)}\n\n${'_'.repeat(50)}\n\n`
      }
    })
  }

  if (styles.answerSheet.includeExplanation) {
    answerSheet += `\n---\n\n# 🔑 Answer Key (For Instructor Reference)\n\n`

    let answerNumber = 1

    if (questionsByType.single_choice && questionsByType.single_choice.length > 0) {
      answerSheet += `## Multiple Choice Answer Key\n\n`
      questionsByType.single_choice.forEach((q, index) => {
        answerSheet += `**${answerNumber + index}.** ${q.correct_answer}\n`
        if (q.explanation) {
          answerSheet += `   *Explanation: ${q.explanation}*\n`
        }
        answerSheet += '\n'
      })
      answerNumber += questionsByType.single_choice.length
    }

    if (questionsByType.cloze && questionsByType.cloze.length > 0) {
      answerSheet += `## Fill-in-the-Blank Answer Key\n\n`
      questionsByType.cloze.forEach((q, index) => {
        answerSheet += `**${answerNumber + index}.** ${q.correct_answer}\n`
        if (q.explanation) {
          answerSheet += `   *Explanation: ${q.explanation}*\n`
        }
        answerSheet += '\n'
      })
      answerNumber += questionsByType.cloze.length
    }

    if (questionsByType.short_answer && questionsByType.short_answer.length > 0) {
      answerSheet += `## Short Answer Reference Answers\n\n`
      questionsByType.short_answer.forEach((q, index) => {
        answerSheet += `**${answerNumber + index}.** ${q.correct_answer}\n`
        if (q.explanation) {
          answerSheet += `   *Notes: ${q.explanation}*\n`
        }
        answerSheet += '\n'
      })
      answerNumber += questionsByType.short_answer.length
    }

    if (questionsByType.auto && questionsByType.auto.length > 0) {
      answerSheet += `## Auto-Generated Question Answer Key\n\n`
      questionsByType.auto.forEach((q, index) => {
        answerSheet += `**${answerNumber + index}.** ${q.correct_answer}\n`
        if (q.explanation) {
          answerSheet += `   *Explanation: ${q.explanation}*\n`
        }
        answerSheet += '\n'
      })
    }
  }

  return answerSheet
}

export const generateCustomMarkdown = (title, questions, styles) => {
  const totalQuestions = questions.length
  const subjects = [...new Set(questions.map(q => q.subject).filter(Boolean))]

  let markdown = ''

  const questionsByType = {
    single_choice: questions.filter(q => q.type === 'single_choice'),
    cloze: questions.filter(q => q.type === 'cloze'),
    short_answer: questions.filter(q => q.type === 'short_answer'),
    auto: questions.filter(q => q.type === 'auto')
  }

  if (!styles.exportOptions.answerSheetOnly) {
    if (styles.header.enabled) {
      markdown += `# ${title}\n\n`

      if (styles.header.subtitle) {
        markdown += `**${styles.header.subtitle}**\n\n`
      }

      markdown += `**Subject:** ${subjects.join(' & ') || 'General'}  \n`
      markdown += `**Duration:** ${styles.header.duration}  \n`
      markdown += `**Total Score:** ${styles.header.totalScore}  \n`
      markdown += `**Total Questions:** ${totalQuestions}  \n\n`

      if (styles.content.includeInstructions) {
        markdown += `---\n\n## 📋 Instructions\n\n`
        markdown += `1. Read all questions carefully before answering\n`
        markdown += `2. Write your answers clearly in the answer sheet\n`
        markdown += `3. Check your work before submission\n\n`
        markdown += `---\n\n`
      }
    }

    let questionNumber = 1

    if (questionsByType.single_choice.length > 0 && styles.sections.singleChoice.enabled) {
      const sectionStyle = styles.sections.singleChoice
      markdown += `## ${sectionStyle.title}\n\n`
      if (sectionStyle.instruction) {
        markdown += `*${sectionStyle.instruction}*\n\n`
      }
      markdown += generateSingleChoiceQuestions(questionsByType.single_choice, questionNumber)
      questionNumber += questionsByType.single_choice.length
    }

    if (questionsByType.cloze.length > 0 && styles.sections.cloze.enabled) {
      const sectionStyle = styles.sections.cloze
      markdown += `\n## ${sectionStyle.title}\n\n`
      if (sectionStyle.instruction) {
        markdown += `*${sectionStyle.instruction}*\n\n`
      }
      markdown += generateClozeQuestions(questionsByType.cloze, questionNumber)
      questionNumber += questionsByType.cloze.length
    }

    if (questionsByType.short_answer.length > 0 && styles.sections.shortAnswer.enabled) {
      const sectionStyle = styles.sections.shortAnswer
      markdown += `\n## ${sectionStyle.title}\n\n`
      if (sectionStyle.instruction) {
        markdown += `*${sectionStyle.instruction}*\n\n`
      }
      markdown += generateShortAnswerQuestions(questionsByType.short_answer, questionNumber)
      questionNumber += questionsByType.short_answer.length
    }

    if (questionsByType.auto.length > 0 && styles.sections.auto.enabled) {
      const sectionStyle = styles.sections.auto
      markdown += `\n## ${sectionStyle.title}\n\n`
      if (sectionStyle.instruction) {
        markdown += `*${sectionStyle.instruction}*\n\n`
      }
      markdown += generateAutoQuestions(questionsByType.auto, questionNumber)
    }
  }

  if (styles.answerSheet.enabled && !styles.exportOptions.questionsOnly) {
    const enabledQuestionsByType = {}
    if (styles.sections.singleChoice.enabled && questionsByType.single_choice.length > 0) {
      enabledQuestionsByType.single_choice = questionsByType.single_choice
    }
    if (styles.sections.cloze.enabled && questionsByType.cloze.length > 0) {
      enabledQuestionsByType.cloze = questionsByType.cloze
    }
    if (styles.sections.shortAnswer.enabled && questionsByType.short_answer.length > 0) {
      enabledQuestionsByType.short_answer = questionsByType.short_answer
    }
    if (styles.sections.auto.enabled && questionsByType.auto.length > 0) {
      enabledQuestionsByType.auto = questionsByType.auto
    }

    markdown += generateCustomAnswerSheet(enabledQuestionsByType, styles)
  }

  return markdown
}

export const downloadMarkdownFile = (content, filename) => {
  const blob = new Blob([content], { type: 'text/markdown;charset=utf-8' })
  const url = window.URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = `${filename}.md`
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  window.URL.revokeObjectURL(url)
}
