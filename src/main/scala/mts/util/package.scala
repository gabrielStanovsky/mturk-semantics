package mts

import scala.util.{Try, Success, Failure}
import scala.collection.mutable
import scala.collection.TraversableOnce

import scala.language.implicitConversions

package object util {

  // Welcome to the new world.
  // The world of ad-hoc refinement types requiring nothing more from the user than a single method call.
  // NO MORE WILL YOU BE UNCERTAIN, ON THE FIRST LINE OF YOUR METHOD,
  // WHETHER THE STRING WAS GUARANTEED TO BE LOWERCASE.
  // FOR YOU HAVE GUARANTEED IT ALREADY IN THE TYPE SYSTEM.
  // This is your weapon. This is your LowerCaseString.
  // Wield it with pride.
  // NOTE: there are projects to help you do refinement typing...but they seem a bit heavier weight for the user..

  // Anyway, don't try to read the code just below. The point is:
  // import mts.util.LowerCaseStrings._
  // and then you get the _.lowerCase method on strings, which yields a LowerCaseString,
  // as well as an implicit conversion from LowerCaseString back to String.
  // In addition, certain uses of existing methods on String will preserve LowerCaseString;
  // if you want there to be more, feel free to let me (Julian) know and I can add them here.
  // I know it seems like weird extra complication, but honestly I was already having bugs from not lowercasing strings,
  // despite sprinkling calls to .toLowerCase around so much that the code had gotten noticeably harder to read.
  protected sealed trait LowerCaseStringCapsule0 {
    type LowerCaseString
    protected[util] sealed trait LowerCaseStringOps {
      def lowerCase(s: String): LowerCaseString
      def +(s1: LowerCaseString, s2: LowerCaseString): LowerCaseString
    }
    protected[util] val LowerCaseStringOpsImpl: LowerCaseStringOps
    implicit def lowerCaseStringToString(lcs: LowerCaseString): String
  }
  protected sealed trait LowerCaseStringCapsule extends LowerCaseStringCapsule0 {
    implicit def wrapLowerCaseString(lcs: LowerCaseString): LowerCaseStringWrapper
    implicit def wrapStringToMakeLowerCase(s: String): StringToLowerCaseWrapper
  }
  val LowerCaseStrings: LowerCaseStringCapsule = new LowerCaseStringCapsule {
    override type LowerCaseString = String
    protected[util] override object LowerCaseStringOpsImpl extends LowerCaseStringOps {
      override def lowerCase(s: String): LowerCaseString = s.toLowerCase
      override def +(s1: LowerCaseString, s2: LowerCaseString) = s1 + s2
    }
    override implicit def lowerCaseStringToString(lcs: LowerCaseString): String =
      lcs
    override implicit def wrapLowerCaseString(lcs: LowerCaseString) =
      new LowerCaseStringWrapper(lcs.asInstanceOf[LowerCaseStrings.LowerCaseString])
    override implicit def wrapStringToMakeLowerCase(s: String) =
      new StringToLowerCaseWrapper(s)
  }
  import LowerCaseStrings.LowerCaseString
  protected class LowerCaseStringWrapper(val lcs: LowerCaseString) extends AnyVal {
    def +(other: LowerCaseString): LowerCaseString = LowerCaseStrings.LowerCaseStringOpsImpl.+(lcs, other)
  }
  protected class StringToLowerCaseWrapper(val s: String) extends AnyVal {
    def lowerCase = LowerCaseStrings.LowerCaseStringOpsImpl.lowerCase(s)
  }

  // Methods I wish were there on existing types. Now they are!

  implicit class RichValForOptions[A](val a: A) extends AnyVal {
    def onlyIf(p: (A => Boolean)): Option[A] = Some(a).filter(p)
    def ifNot(p: (A => Boolean)): Option[A] = Some(a).filterNot(p)
  }

  implicit class RichTry[A](val t: Try[A]) extends AnyVal {
    def toOptionPrinting: Option[A] = t match {
      case Success(a) =>
        Some(a)
      case Failure(e) =>
        System.err.println(e.getLocalizedMessage)
        e.printStackTrace()
        None
    }
  }

  implicit class RichIterator[A](val t: Iterator[A]) extends AnyVal {
    def nextOption: Option[A] = if(t.hasNext) Some(t.next) else None
  }

  // Random utility methods.

  def sendToClipboard(s: String): Unit = {
    import java.awt._;
    import java.awt.datatransfer._;
    import java.io._;
    val selection = new StringSelection(s)
    val clipboard = Toolkit.getDefaultToolkit.getSystemClipboard
    clipboard.setContents(selection, selection)
  }

  def counts[T](xs: TraversableOnce[T]): Map[T, Int] = {
    val m = mutable.HashMap.empty[T, Int].withDefaultValue(0)
    xs.foreach(m(_) += 1)
    m.toMap
  }
}
