#lang racket/base


(require racket/function racket/file racket/path)


(define (gnu-clone)
  (make-directory ".patchiman/a")
  (for-each
    (lambda (path)
      (copy-directory/files
        path
        (build-path (string->path ".patchiman/a") (file-name-from-path path))))
    (filter
      (compose1 not (curry equal? (string->path ".patchiman")))
      (directory-list ".")))
  (delete-directory/files ".patchiman/a/.git" #:must-exist? #t)
  (copy-directory/files ".patchiman/a" ".patchiman/b")
  0)


(provide gnu-clone)
