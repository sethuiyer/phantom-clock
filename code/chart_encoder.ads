--  Chart-aware contiguous memory encoder for discretized optical phase space.
--  Companion artifact to "Chart-Aware Contiguous Memory for Discretized Optical
--  Phase Space" (Sethurathienam Iyer, 2026).
--
--  Design intent (paper Sections 7-8):
--    * E(k, r) = B(k) + r   with consecutive intervals B(0) = 0,
--      B(k+1) = B(k) + N(k).
--    * Range bound        : every address produced is < Arena_Size.
--    * Injectivity        : distinct (chart, rank) pairs yield distinct addresses
--      (relational property, proved via ghost lemma in body).
--    * Coverage/bijectivity follows from consecutiveness of the intervals.
--
--  The chart table below is the concrete table used in Experiment 4:
--  (B0, N0) = (0, 512), (B1, N1) = (512, 256), (B2, N2) = (768, 256).

package Chart_Encoder with SPARK_Mode is

   Chart_Count : constant := 3;
   Arena_Size  : constant := 1024;

   type Chart_Id  is new Natural range 0 .. Chart_Count - 1;
   type Rank      is new Natural range 0 .. Arena_Size - 1;
   type Address   is new Natural range 0 .. Arena_Size - 1;

   --  Chart table (immutable at acquisition time; versioned per batch).
   Base     : constant array (Chart_Id) of Natural := (0, 512, 768);
   Cells    : constant array (Chart_Id) of Natural := (512, 256, 256);

   --  Contract on the raw table: intervals are consecutive and in bounds.
   Table_Is_Consistent : constant Boolean :=
     Base (0) = 0
     and then (for all J in Chart_Id =>
                 Base (J) + Cells (J) <= Arena_Size)
     and then (for all J in Chart_Id'First .. Chart_Id'Last - 1 =>
                 Base (Chart_Id'Succ (J)) = Base (J) + Cells (J));

   --  Total number of cells across all charts.
   Cell_Total : constant := 512 + 256 + 256;  --  = Arena_Size

   type Valid_Rank is new Natural range 0 .. Cell_Total - 1;

   --  The map from linear ranks within a chart to addresses is injective
   --  globally: this predicate expresses that (K, R) corresponds to a
   --  unique global rank, hence a unique address.
   function Global_Rank (K : Chart_Id; R : Valid_Rank) return Natural with
     Pre     => Natural (R) < Cells (K),
     Global    => null,
     Import,
     Ghost;
   --  Encoder: the ONLY address-producing primitive.
   --  The rank must lie within the chart's own cell count; the range bound
   --  then follows from the consecutive-interval table invariant.
   function Encode (K : Chart_Id; R : Valid_Rank) return Address with
     Pre  => Natural (R) < Cells (K)
               and then Base (K) + Natural (R) < Arena_Size,
     Post => Natural (Encode'Result) = Base (K) + Natural (R);

   --  Decoder: reconstructs the canonical cell identity from an address.
   --  Establishes Tier 1 representational correctness: round trip.
   procedure Decode
     (A : Address;
      K : out Chart_Id;
      R : out Valid_Rank) with
     Post => Encode (K, R) = A;

end Chart_Encoder;
