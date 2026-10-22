--  Parameterized chart-table encoder.
--
--  Generalizes code/chart_encoder.ads (a three-entry literal table) to an
--  arbitrary, symbolically-indexed table passed in as a discriminated record.
--  This turns the injectivity claim from "proved for this instance" into a
--  universally quantified contract: for ALL consistent tables up to
--  Max_Charts x Max_Arena.
--
--  Differences from the released instance, all deliberate:
--
--    * No `K_Max - 1` in any range.  The released package could write
--      `0 .. 2` because K_Max was a literal; with a symbolic K_Max the
--      expression `T.K_Max - 1` UNDERFLOWS Chart_Id when K_Max = 0.
--      The tiling is therefore expressed with a K-guarded if-expression,
--      which never evaluates T.Base (K + 1) at K = K_Max.
--
--    * Tables are values, not package constants, so Is_Consistent is a real
--      hypothesis of every contract rather than a decorative constant.
--
--    * Lemma bodies live in the .adb: a ghost lemma proved by induction over
--      adjacent charts, because the SMT solvers only see the pairwise
--      identity Base(K+1) = Base(K) + Cells(K) and will not chain it.

package General_Chart_Encoder with SPARK_Mode is

   Max_Charts : constant := 64;
   Max_Arena  : constant := 65_536;

   type Chart_Id    is range 0 .. Max_Charts - 1;
   type Arena_Bound is range 0 .. Max_Arena;
   type Address     is range 0 .. Max_Arena - 1;

   type Offset_Array is array (Chart_Id range <>) of Arena_Bound;

   type Chart_Table (K_Max : Chart_Id) is record
      Arena_Size : Arena_Bound;
      Base       : Offset_Array (0 .. K_Max);
      Cells      : Offset_Array (0 .. K_Max);
   end record;

   --  The table tiles [0, Arena_Size) exactly:
   --    Base(0) = 0, every Cells(K) > 0, intervals in bounds, every interval
   --    abuts the next, and the last ends precisely at Arena_Size.
   function Is_Consistent (T : Chart_Table) return Boolean is
     (T.Arena_Size > 0
      and then T.Base (0) = 0
      and then (for all K in 0 .. T.K_Max =>
                  T.Cells (K) > 0
                  and then T.Base (K) <= T.Arena_Size - T.Cells (K))
      and then (for all K in 0 .. T.K_Max =>
                  T.Base (K) + T.Cells (K) =
                    (if K < T.K_Max then T.Base (K + 1) else T.Arena_Size)));

   --  The only address-producing primitive.
   function Encode (T : Chart_Table; K : Chart_Id; R : Arena_Bound) return Address with
     Pre  => Is_Consistent (T) and then K <= T.K_Max and then R < T.Cells (K),
     Post => Encode'Result = Address (T.Base (K) + R)
               and then Arena_Bound (Encode'Result) < T.Arena_Size;

   --  Interval K1 ends no later than interval K2 starts.
   procedure Lemma_Monotone (T : Chart_Table; K1, K2 : Chart_Id) with
     Ghost,
     Pre  => Is_Consistent (T) and then K1 < K2 and then K2 <= T.K_Max,
     Post => T.Base (K1) + T.Cells (K1) <= T.Base (K2);

   --  Distinct (chart, rank) pairs never alias.
   procedure Lemma_Injective
     (T  : Chart_Table;
      K1 : Chart_Id;    R1 : Arena_Bound;
      K2 : Chart_Id;    R2 : Arena_Bound) with
     Ghost,
     Pre  => Is_Consistent (T)
               and then K1 <= T.K_Max and then R1 < T.Cells (K1)
               and then K2 <= T.K_Max and then R2 < T.Cells (K2)
               and then Encode (T, K1, R1) = Encode (T, K2, R2),
     Post => K1 = K2 and then R1 = R2;

   procedure Decode
     (T : Chart_Table; A : Address; K : out Chart_Id; R : out Arena_Bound) with
     Pre  => Is_Consistent (T) and then Arena_Bound (A) < T.Arena_Size,
     Post => K <= T.K_Max and then R < T.Cells (K)
               and then Encode (T, K, R) = A;

end General_Chart_Encoder;
